# Permanent Tunnel Setup

DeCloud uses **Tailscale Funnel** for permanent remote access. This gives you a URL like `https://your-machine.tail1234.ts.net` that never changes.

> ⚠️ **Funnel makes DeCloud public.** Anyone on the internet can open the URL, and the only thing between them and your machine is the passcode. **The passcode unlocks a shell on this machine** (terminal, files, updates). Never share it. If only your own devices need access, use [Private-Only Mode](#private-only-mode-no-public-url) (Tailscale Serve) instead.

## Quick Setup

1. **Install Tailscale** (if not already):
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   ```

2. **Start Tailscale**:
   ```bash
   sudo tailscale up
   ```

3. **Enable Funnel for your tailnet (one time, admin console only)**:
   Tailscale ships with Funnel **off**, and no CLI command turns it on. Until
   you enable it, DeCloud starts but never gets a public URL — the phone QR
   code silently never appears.

   - Open [Tailscale admin console → Settings → Funnel](https://login.tailscale.com/admin/settings/funnel).
   - Enable Funnel for your tailnet and save.
   - If your tailnet uses access rules, the machine also needs the `funnel`
     node attribute in the policy file.

4. **Start DeCloud** — it auto-detects Tailscale and starts a **public** Funnel
   (it refuses to if no passcode is set):
   ```bash
   ./decloud start
   ```

Your URL: `https://your-machine-name.tail1234.ts.net`

**Confirm it worked** (do this on a phone that is *not* on your tailnet):
```bash
./decloud status          # → "Tunnel: ✓ active" plus the public URL
tailscale funnel status   # → "Funnel on" and the https://….ts.net URL
curl -I https://your-machine-name.tail1234.ts.net   # → 200, or 302 to the login
```
The last check only works once the tunnel is up; before that it returns
connection errors or a 502. `./decloud funnel-help` repeats these steps at any
time.

## Why Tailscale Funnel?

- **Permanent URL** — never changes, bookmark it
- **End-to-end encrypted** — WireGuard + TLS 1.3
- **Free Tailscale account required** — the free tier is enough
- **Works on any network** — no port forwarding

## Don't share your passcode

The passcode is not a "view-only" password: it unlocks the interactive
terminal, the file manager (including delete/shred) and the self-updater —
in effect, a shell on this machine as your user. Concretely, whoever has it
can:

- **Run commands** in the web terminal, as your user, with your permissions.
- **Read, download, delete or shred** anything the file browser can reach.
- **Change settings** and **install a different version** via the updater.

Treat it like your login password:

- Don't send it to friends or family, or share it alongside the URL or QR code.
- If you think it leaked, change it in Settings (this signs out every device).
- DeCloud is a single-owner app; there are no per-person accounts.

**Stronger options** (same auth model, no code path changes needed):

- Use the longest passcode DeCloud accepts — 10 digits in Settings → Passcode.
  Each extra digit makes guessing 10× harder (8 digits ≈ 100 million
  combinations; 10 digits ≈ 10 billion). Repeated wrong guesses are throttled,
  but length is still the cheapest win.
- Skip the public URL entirely with [Private-Only Mode](#private-only-mode-no-public-url)
  below, so only devices signed in to your tailnet can reach the login screen.

## Alternative: Cloudflare Named Tunnel

If you prefer your own domain (`decloud.yourdomain.com`):

1. Buy a domain (~$10/year) or use a free subdomain
2. Sign up for [Cloudflare](https://cloudflare.com) (free)
3. Add your domain to Cloudflare
4. Run:
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create decloud
   cloudflared tunnel route dns decloud decloud.yourdomain.com
   ```
5. Edit `~/.cloudflared/config.yml`:
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /home/user/.cloudflared/<tunnel-id>.json
   ingress:
     - hostname: decloud.yourdomain.com
       service: http://localhost:8899
     - service: http_status:404
   ```
6. Allow the hostname (DeCloud refuses unknown Host headers), in `.env`:
   ```bash
   DECLOUD_ALLOWED_HOSTS=decloud.yourdomain.com
   ```
7. Start: `cloudflared tunnel run`

The same warning applies: this is public, and the passcode is a shell.

## Private-Only Mode (No Public URL)

Recommended if only your own devices need DeCloud. Tailscale Serve gives
HTTPS on your tailnet only — nothing is reachable from the internet:

1. Don't run `./decloud start` (it starts the public Funnel); the service
   installed by `install.sh` runs the app. If a Funnel is on, turn it off:
   `sudo tailscale funnel --https=443 off`
2. Serve it to your tailnet:
   ```bash
   sudo tailscale serve --bg http://localhost:8899
   ```
3. Open `https://your-machine.tail1234.ts.net` from any device signed in to
   your tailnet.

## Troubleshooting

**"Funnel failed" / no public URL / no QR code**

The most common cause by far is Funnel not being enabled for your tailnet —
Tailscale requires the admin console for that, and DeCloud can only report it:

1. Open [Tailscale admin console → Settings → Funnel](https://login.tailscale.com/admin/settings/funnel)
   and enable Funnel for your tailnet.
2. Check Tailscale is running and logged in: `tailscale status`.
3. Restart: `sudo ./decloud restart`, then `./decloud qr`.
4. Still stuck? `./decloud funnel-help` prints the walkthrough, and running
   `sudo tailscale funnel --bg --https=443 http://localhost:8899` by hand shows
   Tailscale's exact error.

**"URL not working"**
- Wait 30 seconds for DNS propagation
- Check: `curl -I https://your-machine.tail1234.ts.net`
- Regenerate QR: `./decloud qr`

**"Can't open it from my phone"**
- Make sure you use the full URL (including `https://`)
- Check your passcode is correct
- Verify funnel is on: `tailscale funnel status`
