"""Independent CPU ray-cast ground truth; candidate estimators never receive this module's poses/masks."""
import numpy as np
import cv2
W,H=832,480
K=np.array([[600.,0,416.],[0,600.,240.],[0,0,1.]])
def rotation(theta):
    c,s=np.cos(theta),np.sin(theta)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]],dtype=np.float64)
def project(world,theta):
    p=np.asarray(world)@rotation(theta).T
    uv=np.column_stack((600*p[:,0]/p[:,2]+416,600*p[:,1]/p[:,2]+240))
    return uv,p[:,2]
class Scene:
    def __init__(self,seed,case):
        self.seed=seed; self.case=case; self.family=case['family']; self.textures={}
        self.angles=np.arange(97,dtype=np.float64)*case['step']
        if case.get('reverse'): self.angles=self.angles[::-1].copy()
        u,v=np.meshgrid(np.arange(W,dtype=float),np.arange(H,dtype=float))
        self.pixels=np.column_stack((u.ravel(),v.ravel()))
        u,v=np.meshgrid(np.arange(4,W,8,dtype=float),np.arange(4,H,8,dtype=float))
        self.grid=np.column_stack((u.ravel(),v.ravel()))
    def raycast(self,uv,index):
        uv=np.asarray(uv,dtype=float); rays=np.column_stack(((uv[:,0]-416)/600,(uv[:,1]-240)/600,np.ones(len(uv))))@rotation(self.angles[index])
        dz=rays[:,2]; valid=dz>1e-8
        xyz=rays*(12/np.where(valid,dz,1))[:,None]; ids=np.zeros(len(uv),np.int16); ids[~valid]=-1
        # A bounded nearer static textured rectangle produces true visibility transitions.
        middle=rays*(7/np.where(valid,dz,1))[:,None]
        offset=.20 if self.seed==41029 else -.15
        take=valid&(middle[:,0]>-1.4+offset)&(middle[:,0]<1.1+offset)&(np.abs(middle[:,1])<1.7)
        xyz[take]=middle[take]; ids[take]=1
        if self.family=='occlusion':
            near=rays*(3/np.where(valid,dz,1))[:,None]
            width=.9 if self.seed==41029 else .8
            take=valid&(np.abs(near[:,0]-self.occluder_center(index))<width)&(np.abs(near[:,1])<2)
            xyz[take]=near[take]; ids[take]=2
        # The finite world has a known field-of-view boundary.
        valid&=(np.abs(xyz[:,0])<100)&(np.abs(xyz[:,1])<40)
        ids[~valid]=-1
        return xyz,ids
    def occluder_center(self,index):
        return (1.4 if self.seed==41029 else 1.2)*np.sin(2*np.pi*index/96)
    def texture_state(self,xyz,ids,index):
        valid=(ids>=0)&(ids!=2)
        if self.family=='blank' and 32<=index<=47: valid[:]=False
        if self.family=='attrition':
            # World-anchored hashed patches disappear in four prespecified stages.
            xx=np.floor(xyz[:,0]*2).astype(np.int64); yy=np.floor(xyz[:,1]*2).astype(np.int64)
            bucket=np.mod(xx*37+yy*17+ids*13+self.seed,16)/16
            valid&=bucket<[1,.75,.5,.25][min(index//24,3)]
        epoch=index if self.family=='changing_texture' else 0
        return valid,epoch
    def texture(self,obj,epoch):
        key=(int(obj),int(epoch))
        if key not in self.textures:
            rng=np.random.default_rng(self.seed+obj*1031+epoch*100003)
            noise=rng.integers(0,256,(512,512),dtype=np.uint8)
            smooth=cv2.GaussianBlur(noise,(0,0),.8)
            # High-contrast but irregular patches, stationary in world coordinates.
            texture=np.clip((smooth.astype(float)-128)*3+128,0,255).astype(np.uint8)
            self.textures={k:v for k,v in self.textures.items() if k[1]==epoch}
            self.textures[key]=texture
        return self.textures[key]
    def render(self,index):
        xyz,ids=self.raycast(self.pixels,index); textured,epoch=self.texture_state(xyz,ids,index)
        image=np.full((H,W),100,np.uint8)
        for obj in [0,1]:
            mx=(xyz[:,0]*60).astype(np.float32).reshape(H,W); my=(xyz[:,1]*60).astype(np.float32).reshape(H,W)
            tex=cv2.remap(self.texture(obj,epoch),mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
            take=((ids==obj)&textured).reshape(H,W); image[take]=tex[take]
        image[ids.reshape(H,W)==2]=50
        image[ids.reshape(H,W)<0]=25
        if self.family=='blank' and 32<=index<=47: image[:]=70 if index%2 else 140
        return np.repeat(image[:,:,None],3,axis=2),ids.reshape(H,W),textured.reshape(H,W)
    def truth(self,uv,index):
        xyz,ids=self.raycast(uv,index)
        transported=xyz.copy()
        if self.family=='occlusion': transported[ids==2,0]+=self.occluder_center(index+1)-self.occluder_center(index)
        to,depth=project(transported,self.angles[index+1])
        inside=(depth>0)&np.isfinite(to).all(axis=1)&(to[:,0]>=0)&(to[:,0]<W)&(to[:,1]>=0)&(to[:,1]<H)
        nextxyz,nextids=self.raycast(np.nan_to_num(to),index+1)
        visible=(ids>=0)&inside&(ids==nextids)&(np.linalg.norm(transported-nextxyz,axis=1)<1e-6)
        t0,e0=self.texture_state(xyz,ids,index); t1,e1=self.texture_state(xyz,ids,index+1)
        support=visible&t0&t1&(e0==e1)
        return {'world':xyz,'object_id':ids,'to_xy':to,'flow':to-np.asarray(uv),'visible':visible,'support':support,'occluded':inside&(ids>=0)&~visible,'offscreen':(ids>=0)&~inside}
