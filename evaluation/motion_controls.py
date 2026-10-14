import datetime
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np

WIDTH,HEIGHT=832,480
PARAMETERS={'maxCorners':200,'qualityLevel':.01,'minDistance':7,'blockSize':7}
LK={'winSize':(21,21),'maxLevel':3,'criteria':(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.01)}

def make_mask(rectangles):
    mask=np.zeros((HEIGHT,WIDTH),np.uint8)
    for x0,y0,x1,y1 in rectangles: mask[y0:y1,x0:x1]=255
    return mask

def track(frames,mask):
    first=cv2.cvtColor(np.asarray(frames[0]),cv2.COLOR_RGB2GRAY)
    points=cv2.goodFeaturesToTrack(first,mask=mask,**PARAMETERS)
    if points is None: points=np.empty((0,1,2),np.float32)
    initial=points[:,0].copy(); ids=np.arange(len(points)); intervals=[]
    for index in range(len(frames)-1):
        a=cv2.cvtColor(np.asarray(frames[index]),cv2.COLOR_RGB2GRAY)
        b=cv2.cvtColor(np.asarray(frames[index+1]),cv2.COLOR_RGB2GRAY)
        row={'from_frame':index,'to_frame':index+1,'incoming_tracks':len(points),'eligible':False}
        if len(points):
            nxt,forward_status,_=cv2.calcOpticalFlowPyrLK(a,b,points,None,**LK)
            if nxt is None:
                points=np.empty((0,1,2),np.float32); ids=ids[:0]
            else:
                back,back_status,_=cv2.calcOpticalFlowPyrLK(b,a,nxt,None,**LK)
                if back is None:
                    points=np.empty((0,1,2),np.float32); ids=ids[:0]
                else:
                    error=np.linalg.norm(back[:,0]-points[:,0],axis=1)
                    finite=np.isfinite(nxt).all(axis=(1,2)) & np.isfinite(back).all(axis=(1,2))
                    bounds=(nxt[:,0,0]>=0)&(nxt[:,0,0]<WIDTH)&(nxt[:,0,1]>=0)&(nxt[:,0,1]<HEIGHT)
                    valid=(forward_status[:,0]==1)&(back_status[:,0]==1)&finite&bounds&(error<=1)
                    old=points[valid,0]; current=nxt[valid,0]; ids=ids[valid]
                    displacement=current[:,0]-old[:,0]
                    cells=set((int(x//(WIDTH/4)),int(y//(HEIGHT/4))) for x,y in current)
                    row.update({'surviving_tracks':len(current),'grid_cells':len(cells),
                                'track_ids':ids.tolist(),'from_xy':old.tolist(),'to_xy':current.tolist(),
                                'forward_backward_errors':error[valid].tolist(),
                                'horizontal_displacements_pixels':displacement.tolist()})
                    row['eligible']=len(current)>=20 and len(cells)>=4
                    row['median_horizontal_displacement_over_width']=float(np.median(displacement)/WIDTH) if row['eligible'] else None
                    points=current[:,None].astype(np.float32)
        row.setdefault('surviving_tracks',0); row.setdefault('grid_cells',0)
        row.setdefault('median_horizontal_displacement_over_width',None)
        intervals.append(row)
    values=[r['median_horizontal_displacement_over_width'] for r in intervals if r['eligible']]
    return {'initial_points_xy':initial.tolist(),'intervals':intervals,'total_intervals':len(intervals),
            'eligible_intervals':len(values),'invalid_intervals':[r['from_frame'] for r in intervals if not r['eligible']],
            'coverage':len(values)/len(intervals) if intervals else 0,
            'motion_proxy':float(np.median(values)) if values else None,'parameters':{**PARAMETERS,'LK':str(LK),
            'forward_backward_error_pixels':1,'minimum_survivors':20,'minimum_4x4_cells':4},
            'initial_landmarks_only_no_reseeding':True}

def reference_frames(direction):
    rng=np.random.default_rng(20261014)
    xyz=np.array([(x,y,5.) for y in np.linspace(-1.6,1.6,8) for x in np.linspace(-2.8,2.8,12)])
    textures=rng.integers(60,256,size=(len(xyz),9,9),dtype=np.uint8)
    frames=[]; projected=[]
    for step in range(5):
        yaw=direction*.03*step; c,s=np.cos(yaw),np.sin(yaw)
        rotation=np.array([[c,0,s],[0,1,0],[-s,0,c]])
        p=xyz@rotation.T
        xy=np.column_stack((600*p[:,0]/p[:,2]+416,600*p[:,1]/p[:,2]+240)); projected.append(xy.tolist())
        image=np.zeros((HEIGHT,WIDTH),np.uint8)
        for (x,y),texture in zip(xy,textures):
            ix,iy=int(round(x)),int(round(y))
            if 5<=ix<WIDTH-5 and 5<=iy<HEIGHT-5: image[iy-4:iy+5,ix-4:ix+5]=texture
        frames.append(np.repeat(image[:,:,None],3,axis=2))
    return np.stack(frames),{'points_3D':xyz.tolist(),'projected_xy':projected,'yaw_per_step_radians':direction*.03,
                             'world_to_camera':True,'fx':600,'fy':600,'cx':416,'cy':240}

def execute_controls(base):
    target=base/'metric_controls.json'; assert not target.exists()
    out=base/'metric_control_inputs'; out.mkdir(exist_ok=False)
    mask=make_mask([[24,24,808,456]])
    rows={}; frames_by_name={}
    for name,direction in [('positive_yaw',1),('negative_yaw',-1),('identity',0)]:
        frames,geometry=reference_frames(direction); frames_by_name[name]=frames
        np.save(out/f'{name}.npy',frames,allow_pickle=False)
        rows[name]={'geometry':geometry,'tracking':track(frames,mask)}
    negative=frames_by_name['identity'].copy()
    # Deliberately replace the initially textured image with changing spatially
    # uniform textures. There is no geometric camera motion to recover.
    for i in range(1,len(negative)): negative[i].fill(255 if i%2 else 0)
    np.save(out/'changing_texture_negative.npy',negative,allow_pickle=False)
    rows['changing_texture_negative']={'definition':'Textured initial grid followed by alternating uniform intensities; no geometric motion',
                                      'tracking':track(negative,mask)}
    dp=rows['positive_yaw']['tracking']['motion_proxy']; dn=rows['negative_yaw']['tracking']['motion_proxy']
    di=rows['identity']['tracking']['motion_proxy']
    checks={'positive_yaw_moves_right':dp is not None and dp>0,'negative_yaw_moves_left':dn is not None and dn<0,
            'identity_repeat_has_zero_median_motion':di==0,
            'action_label_swap_is_detected':dp is not None and dn is not None and not(dp<0 or dn>0),
            'non_geometric_texture_change_is_non_evaluable':rows['changing_texture_negative']['tracking']['eligible_intervals']==0}
    result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'synthetic_controls':True,
            'no_Astra_outputs_used_for_tuning':True,'rows':rows,'checks':checks,
            'action_label_swap':{'construction':'Relabel the positive and negative reference sequences with opposite action names',
                                  'positive_reference_relabelled_negative_proxy':dp,'negative_reference_relabelled_positive_proxy':dn},
            'status':'CONTROLS_PASSED' if all(checks.values()) else 'CONTROLS_FAILED'}
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':checks,'proxies':{'positive':dp,'negative':dn,'identity':di}}),flush=True)
    return result

if __name__=='__main__': execute_controls(Path(__file__).resolve().parent)
