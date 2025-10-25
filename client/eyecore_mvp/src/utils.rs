use sha2::{Sha256, Digest};

#[allow(dead_code)]
pub fn hash_data(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    format!("{:x}", hasher.finalize())
}

#[allow(dead_code)]
pub fn anonymize_text(text: &str) -> String {
    // Create a hash-based pseudonym for anonymization
    let hash = hash_data(text.as_bytes());
    format!("anon_{}", &hash[..8])
}
