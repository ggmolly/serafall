#!/usr/bin/env python3
import sys,argparse,os
def gf_mul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a <<=1
        if a & 0x100: a ^= 0x11b
        b >>=1
    return r & 0xff
def gf_inv(a):
    if a==0: raise ZeroDivisionError
    return gf_pow(a,254)
def gf_pow(a,e):
    r=1
    while e:
        if e&1: r=gf_mul(r,a)
        a=gf_mul(a,a); e//=2
    return r
def lagrange_at_zero(xs):
    k=len(xs)
    res=[]
    for i in range(k):
        num=1
        den=1
        xi=xs[i]
        for j in range(k):
            if i==j: continue
            xj=xs[j]
            num=gf_mul(num,xj)
            den=gf_mul(den, xj ^ xi)
        res.append(gf_mul(num, gf_inv(den)))
    return res
def parse_share_file(path):
    s=open(path,"r").read().strip()
    ix_hex,hexdata = s.split(":",1)
    idx=int(ix_hex,16)
    data=bytes.fromhex(hexdata.strip())
    return idx,data
def combine(paths,t,out):
    pts=[]
    for p in paths:
        idx,data=parse_share_file(p)
        pts.append((idx,data))
    if len(pts)<t: raise SystemExit("need >= t shares")
    pts=pts[:t]
    xs=[x for x,_ in pts]
    coeffs=lagrange_at_zero(xs)
    L=len(pts[0][1])
    for _,d in pts:
        if len(d)!=L: raise SystemExit("share length mismatch")
    outb=bytearray(L)
    for i in range(L):
        v=0
        for j,(_,d) in enumerate(pts):
            v ^= gf_mul(d[i], coeffs[j])
        outb[i]=v
    open(out,"wb").write(bytes(outb))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("-t",type=int,required=True)
    p.add_argument("-o","--out",required=True)
    p.add_argument("shares",nargs="+")
    args=p.parse_args()
    combine(args.shares, args.t, args.out)
if __name__=="__main__":
    main()

