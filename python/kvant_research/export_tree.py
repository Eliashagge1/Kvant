from pathlib import Path
import argparse,hashlib,json,os,subprocess

def main():
 p=argparse.ArgumentParser();p.add_argument("--model",required=True);p.add_argument("--output",required=True);p.add_argument("--features",nargs="+",required=True);p.add_argument("--private-key",required=True);a=p.parse_args()
 import treelite,tl2cgen
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True);model=treelite.Model.load(a.model,model_format="xgboost_json");lib=out/"model.so";tl2cgen.export_lib(model,toolchain="gcc",libpath=str(lib));sig=out/"model.so.sig";subprocess.run(["openssl","pkeyutl","-sign","-rawin","-inkey",a.private_key,"-in",str(lib),"-out",str(sig)],check=True)
 manifest={"schema_version":2,"kind":"tl2cgen","artifact":lib.name,"signature":sig.name,"sha256":hashlib.sha256(lib.read_bytes()).hexdigest(),"feature_names":a.features};tmp=out/"manifest.json.tmp";tmp.write_text(json.dumps(manifest,indent=2));os.replace(tmp,out/"manifest.json")
if __name__=="__main__":main()
