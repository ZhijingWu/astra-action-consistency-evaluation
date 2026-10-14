import math,hashlib
import numpy as np
import cv2
from geometry import Scene,rotation,project
def run(config):
    checks={}; evidence={}; rng=np.random.default_rng(2026101401)
    xyz=np.column_stack((rng.uniform(-2,2,1000),rng.uniform(-1.5,1.5,1000),rng.uniform(5,15,1000)))
    # Independent rational pinhole formula; does not call renderer rotation/project.
    maxerr=0.
    for angle in [-.3,-.1,0,.1,.3]:
        uv,z=project(xyz,angle); x=xyz[:,0]/xyz[:,2]; y=xyz[:,1]/xyz[:,2]
        s,c=math.sin(angle),math.cos(angle)
        direct=np.column_stack((600*(x*c+s)/(c-x*s)+416,600*y/(c-x*s)+240))
        maxerr=max(maxerr,float(np.max(np.abs(uv-direct))))
    checks['independent_projection_formula']=maxerr<1e-9; evidence['max_projection_error_pixels']=maxerr
    center=np.array([[0.,0.,8.]])
    up,_=project(center,.1); un,_=project(center,-.1)
    checks['independent_central_sign']=bool(up[0,0]>416 and un[0,0]<416 and abs(up[0,0]-(416+600*math.tan(.1)))<1e-9)
    # A separate Rodrigues implementation represents physical camera heading.
    reversed_R,_=cv2.Rodrigues(np.array([0.,-.1,0.])); p=center@reversed_R.T
    u=600*p[0,0]/p[0,2]+416
    checks['physical_convention_reversal']=bool(u<416 and abs(u-un[0,0])<1e-9)
    checks['deliberate_sign_metadata_swap_detected']=bool(not(up[0,0]<416 or un[0,0]>416))
    checks['proper_rotation']=all(np.max(np.abs(rotation(a).T@rotation(a)-np.eye(3)))<1e-12 and abs(np.linalg.det(rotation(a))-1)<1e-12 for a in [-.864,0,.864])
    checks['identity_zero_flow']=True; checks['forward_backward_geometry']=True; checks['repeat_render_byte_identical']=True
    checks['visible_projection_consistency']=True; maxfb=0.; occluded=0; offscreen=0
    for seed in config['splits'].values():
        for name in ['zero','large_positive','large_negative','occlusion_positive','occlusion_negative','attrition_positive']:
            case=next(c for c in config['cases'] if c['name']==name); scene=Scene(seed,case)
            image,_,_=scene.render(0); again,_,_=Scene(seed,case).render(0)
            checks['repeat_render_byte_identical']&=bool(np.array_equal(image,again))
            for i in [0,24,48,72,95]:
                t=scene.truth(scene.grid,i); occluded+=int(t['occluded'].sum()); offscreen+=int(t['offscreen'].sum())
                if name=='zero': checks['identity_zero_flow']&=bool(np.max(np.abs(t['flow']))<1e-9)
                if t['visible'].any():
                    nextworld,nextids=scene.raycast(t['to_xy'][t['visible']],i+1)
                    if scene.family=='occlusion': nextworld[nextids==2,0]-=scene.occluder_center(i+1)-scene.occluder_center(i)
                    back,_=project(nextworld,scene.angles[i]); e=float(np.max(np.abs(back-scene.grid[t['visible']])))
                    maxfb=max(maxfb,e); checks['forward_backward_geometry']&=e<1e-8
                    checks['visible_projection_consistency']&=bool(np.all(nextids==t['object_id'][t['visible']]))
                checks['visible_projection_consistency']&=bool(not np.any(t['support']&(t['occluded']|t['offscreen'])))
    checks['occlusion_and_departure_exercised']=occluded>0 and offscreen>0
    evidence.update({'max_geometric_FB_error_pixels':maxfb,'excluded_occluded_grid_samples':occluded,'excluded_offscreen_grid_samples':offscreen,'central_positive_theta_dx_pixels':float(up[0,0]-416),'central_negative_theta_dx_pixels':float(un[0,0]-416),'physical_positive_heading_dx_pixels':float(u-416),'independent_formula':'u_next=f*(x cos(delta)+sin(delta))/(cos(delta)-x sin(delta))+cx; positive central theta gives +f tan(theta)'})
    return {'checks':{k:bool(v) for k,v in checks.items()},'evidence':evidence,'all_passed':bool(all(checks.values()))}
