"""Image-only M1/M2. No geometry import, poses, masks, depth or action supplied."""
import cv2
import numpy as np
W,H=832,480
PARAMETERS={'qualityLevel':.01,'minDistance':7,'blockSize':7}
LK={'winSize':(21,21),'maxLevel':3,'criteria':(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,.01)}
def cells(points): return len(set((int(x//208),int(y//120)) for x,y in points))
def detect(gray,existing=None):
    mask=np.zeros((H,W),np.uint8); mask[12:H-12,12:W-12]=255
    if existing is not None:
        for x,y in existing: cv2.circle(mask,(round(float(x)),round(float(y))),7,0,-1)
    points=[]
    for row in range(4):
        for col in range(4):
            tile=np.zeros_like(mask); tile[row*120:(row+1)*120,col*208:(col+1)*208]=mask[row*120:(row+1)*120,col*208:(col+1)*208]
            p=cv2.goodFeaturesToTrack(gray,maxCorners=20,mask=tile,**PARAMETERS)
            if p is not None: points.extend(p[:,0])
    return np.asarray(points,dtype=np.float32).reshape(-1,2)
def step(a,b,points):
    n=len(points)
    if not n: return np.empty((0,2),np.float32),np.zeros(0,bool),np.array([]),np.array([])
    nxt,fs,_=cv2.calcOpticalFlowPyrLK(a,b,points[:,None],None,**LK)
    if nxt is None: return np.zeros_like(points),np.zeros(n,bool),np.full(n,np.nan),np.full(n,np.nan)
    back,bs,_=cv2.calcOpticalFlowPyrLK(b,a,nxt,None,**LK)
    if back is None: return nxt[:,0],np.zeros(n,bool),np.full(n,np.nan),np.full(n,np.nan)
    nxt=nxt[:,0]; fb=np.linalg.norm(back[:,0]-points,axis=1)
    ok=(fs[:,0]==1)&(bs[:,0]==1)&np.isfinite(nxt).all(axis=1)&np.isfinite(back[:,0]).all(axis=1)&(nxt[:,0]>=0)&(nxt[:,0]<W)&(nxt[:,1]>=0)&(nxt[:,1]<H)&(fb<=1)
    ncc=np.full(n,np.nan)
    for i in np.flatnonzero(ok):
        # Compare normalized local appearance, independent of geometric truth.
        x=cv2.getRectSubPix(a,(7,7),tuple(map(float,points[i]))).astype(float).ravel(); x-=x.mean()
        y=cv2.getRectSubPix(b,(7,7),tuple(map(float,nxt[i]))).astype(float).ravel(); y-=y.mean()
        den=np.linalg.norm(x)*np.linalg.norm(y)
        ncc[i]=float(x@y/den) if den>1e-8 else -1
    ok&=ncc>=.85
    return nxt,ok,fb,ncc
class Estimator:
    def __init__(self,method): self.method=method; self.points=np.empty((0,2),np.float32); self.born=np.empty(0,int); self.ids=np.empty(0,int); self.next_id=0
    def update(self,a,b,index):
        refreshed=0
        if self.method=='M2' or index%8==0:
            fresh=detect(a,None if self.method=='M2' else self.points)
            if self.method=='M2': self.points=np.empty((0,2),np.float32); self.born=np.empty(0,int); self.ids=np.empty(0,int)
            fresh=fresh[:max(0,320-len(self.points))]; refreshed=len(fresh)
            self.points=np.concatenate([self.points,fresh]); self.born=np.concatenate([self.born,np.full(refreshed,index,int)])
            self.ids=np.concatenate([self.ids,np.arange(self.next_id,self.next_id+refreshed)]); self.next_id+=refreshed
        incoming=len(self.points); nxt,ok,fb,ncc=step(a,b,self.points)
        old=self.points[ok]; cur=nxt[ok]; ids=self.ids[ok]; age=index-self.born[ok]+1
        dx=cur[:,0]-old[:,0]; g=cells(cur)
        ratio=len(cur)/incoming if incoming else 0
        reasons=[]
        if len(cur)<40: reasons.append('COUNT')
        if g<6: reasons.append('GRID')
        if ratio<.5: reasons.append('ACCEPTANCE_FRACTION')
        valid=not reasons; value=float(np.median(dx)) if valid else None
        row={'method':self.method,'from_frame':index,'to_frame':index+1,'incoming':incoming,'accepted':len(cur),'refreshed_features':refreshed,'grid_cells':g,'acceptance_fraction':ratio,'valid':valid,'abstention_reason':'+'.join(reasons) if reasons else '',
             'signed_dx_pixels':value,'signed_dx_over_width':value/W if value is not None else None,'direction':int(np.sign(value)) if value is not None and abs(value)>.25 else 0 if valid else None,
             'track_age_median_intervals':float(np.median(age)) if len(age) else None,'track_age_max_intervals':int(age.max()) if len(age) else None,
             'median_FB_pixels':float(np.median(fb[ok])) if len(cur) else None,'median_patch_NCC':float(np.median(ncc[ok])) if len(cur) else None,
             'dx_IQR_pixels':float(np.percentile(dx,75)-np.percentile(dx,25)) if len(dx) else None}
        detail={'ids':ids,'from_xy':old,'to_xy':cur,'age':age,'FB':fb[ok],'NCC':ncc[ok]}
        self.points=cur; self.born=self.born[ok]; self.ids=ids
        return row,detail
