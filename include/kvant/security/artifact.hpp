#pragma once
#include <filesystem>
#include <string>
namespace kvant::security {
[[nodiscard]]std::string sha256_file(const std::filesystem::path&);
[[nodiscard]]bool verify_ed25519(const std::filesystem::path&artifact,const std::filesystem::path&signature,const std::filesystem::path&public_key_pem);
void enforce_safe_artifact_path(const std::filesystem::path&artifact,const std::filesystem::path&allowlisted_root);
}
