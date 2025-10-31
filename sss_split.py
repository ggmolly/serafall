#!/usr/bin/env python3
import sys,os,secrets,argparse
def gf_mul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a <<=1
        if a & 0x100: a ^= 0x11b
        b >>=1
    return r & 0xff
def gf_pow(a,e):
    r=1
    while e:
        if e&1: r=gf_mul(r,a)
        a=gf_mul(a,a); e//=2
    return r
def eval_poly(coeffs,x):
    res=0
    for c in reversed(coeffs):
        res = gf_mul(res,x) ^ c
    return res
def split(secret_bytes,t,n):
    L=len(secret_bytes)
    shares=[bytearray() for _ in range(n)]
    for i in range(L):
        coeffs=[secret_bytes[i]] + [secrets.randbelow(256) for _ in range(t-1)]
        for x in range(1,n+1):
            shares[x-1].append(eval_poly(coeffs,x))
    return shares
def write_shares(shares,outdir):
    os.makedirs(outdir,exist_ok=True)
    for idx,buf in enumerate(shares,start=1):
        name=f"share_{idx:02d}.txt"
        path=os.path.join(outdir,name)
        with open(path,"w") as f:
            f.write(f"{idx:02x}:{buf.hex()}\n")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("-t",type=int,required=True)
    p.add_argument("-n",type=int,required=True)
    p.add_argument("-i","--input",required=True)
    p.add_argument("-o","--outdir",required=True)
    args=p.parse_args()
    if not (2<=args.t<=args.n<=255): sys.exit("invalid t/n")
    with open(args.input,"rb") as f: secret=f.read()
    shares=split(secret,args.t,args.n)
    write_shares(shares,args.outdir)
if __name__=="__main__":
    main()

