# Catatan: Setup GitHub via SSH (Bare Metal)

Dokumen ini merangkum langkah setup GitHub SSH untuk repo `hris` agar bisa `git push/pull` tanpa password.

## 1) Set remote repo ke SSH

```bash
cd /home/ruben/horillas/hris
git remote set-url origin git@github.com:rhgmanik/hris.git
git remote -v
```

## 2) Generate SSH key (ed25519)

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "rhgmanik@users.noreply.github.com" -f ~/.ssh/id_ed25519 -N ""
```

Public key bisa dilihat dengan:

```bash
cat ~/.ssh/id_ed25519.pub
```

## 3) Tambahkan SSH key ke GitHub

- Buka GitHub → **Settings** → **SSH and GPG keys**
- Klik **New SSH key**
- Isi:
  - **Title**: mis. `horilla-deploy-server`
  - **Key type**: Authentication Key
  - **Key**: paste isi `~/.ssh/id_ed25519.pub`
- Klik **Add SSH key**

## 4) Test koneksi SSH ke GitHub

```bash
ssh -T git@github.com
```

Jika sukses, GitHub akan menampilkan pesan autentikasi berhasil (biasanya menyebut username).

## 5) Push repository pertama kali

```bash
cd /home/ruben/horillas/hris
git push -u origin main
```

## 6) Troubleshooting cepat

- **Permission denied (publickey)**:
  - pastikan SSH key sudah ditambahkan di GitHub.
  - cek key yang dipakai SSH:

    ```bash
    ssh -vT git@github.com
    ```

- **Host key warning** (pertama kali connect):
  - normal; bisa accept host key `github.com`.

