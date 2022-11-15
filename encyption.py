from Crypto.Cipher import AES


class Encryption:
    def __init__(self, key):
        self._key = b""
        self.key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value.to_bytes(16, "little")

    def encrypt(self, plaintext: str) -> tuple[str, str, str]:
        """
        Encrypts a plaintext with AES
        :param plaintext: String to encrypt
        :return: ciphertext, tag and nonce as hex strings
        """
        cipher = AES.new(self.key, AES.MODE_EAX)
        ct, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        return ct.hex(), tag.hex(), cipher.nonce.hex()

    def decrypt(self, ciphertext: str, tag: str, nonce: str) -> str | bool:
        """
        Decrypts a HEX string with AES
        :param ciphertext: The ciphertext to decrypt
        :param tag: The tag to verify decryption
        :param nonce: The nonce to use for decryption
        :return: The decrypted string or False if the decryption failed
        """
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=bytes.fromhex(nonce))
        plaintext = cipher.decrypt(bytes.fromhex(ciphertext))

        try:
            cipher.verify(bytes.fromhex(tag))
        except ValueError:
            return False

        return plaintext.decode("utf-8")


def main():
    key = 15
    enc = Encryption(key)
    ct, tag, nonce = enc.encrypt("Hello World")
    print(ct, tag, nonce)
    print(enc.decrypt(ct, tag, nonce))


if __name__ == '__main__':
    main()
