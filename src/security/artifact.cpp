#include "kvant/security/artifact.hpp"
#include <openssl/evp.h>
#include <openssl/pem.h>
#include <fstream>
#include <iomanip>
#include <memory>
#include <sstream>
#include <stdexcept>
namespace kvant::security {namespace {using Ctx=std::unique_ptr<EVP_MD_CTX,decltype(&EVP_MD_CTX_free)>;using Key=std::unique_ptr<EVP_PKEY,decltype(&EVP_PKEY_free)>;std::vector<unsigned char>bytes(const std::filesystem::path&p){std::ifstream f(p,std::ios::binary);if(!f)throw std::runtime_error("cannot open file");return{std::istreambuf_iterator<char>(f),{}};}}
std::string sha256_file(const std::filesystem::path&p){auto data=bytes(p);unsigned char h[EVP_MAX_MD_SIZE];unsigned n=0;Ctx c(EVP_MD_CTX_new(),EVP_MD_CTX_free);if(!c||EVP_DigestInit_ex(c.get(),EVP_sha256(),nullptr)!=1||EVP_DigestUpdate(c.get(),data.data(),data.size())!=1||EVP_DigestFinal_ex(c.get(),h,&n)!=1)throw std::runtime_error("SHA-256 failure");std::ostringstream o;for(unsigned i=0;i<n;++i)o<<std::hex<<std::setw(2)<<std::setfill('0')<<int(h[i]);return o.str();}
bool verify_ed25519(const std::filesystem::path&a,const std::filesystem::path&s,const std::filesystem::path&pem){auto data=bytes(a),sig=bytes(s);FILE*f=fopen(pem.c_str(),"rb");if(!f)throw std::runtime_error("cannot open public key");Key key(PEM_read_PUBKEY(f,nullptr,nullptr,nullptr),EVP_PKEY_free);fclose(f);if(!key)throw std::runtime_error("invalid public key");Ctx c(EVP_MD_CTX_new(),EVP_MD_CTX_free);if(!c||EVP_DigestVerifyInit(c.get(),nullptr,nullptr,nullptr,key.get())!=1)throw std::runtime_error("signature init failed");return EVP_DigestVerify(c.get(),sig.data(),sig.size(),data.data(),data.size())==1;}
void enforce_safe_artifact_path(const std::filesystem::path&a,const std::filesystem::path&r){auto ac=std::filesystem::weakly_canonical(a),rc=std::filesystem::weakly_canonical(r);auto as=ac.native(),rs=rc.native();if(as.size()<=rs.size()||as.compare(0,rs.size(),rs)!=0||as[rs.size()]!=std::filesystem::path::preferred_separator)throw std::runtime_error("artifact path outside allowlisted root");auto status=std::filesystem::status(ac);if((status.permissions()&std::filesystem::perms::others_write)!=std::filesystem::perms::none)throw std::runtime_error("artifact is world-writable");}
}
