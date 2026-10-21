# Backup, local installation, and rollback

These instructions apply to the existing, working IMX462 application/service layout on the tested X5. They are not a first-boot installer for a new board. No installation, service restart, or reboot was performed while preparing this public release.

Use separately obtained SDK components and local generated files only under the applicable permissions. The public source release does not authorize redistribution of those files. First complete the local build and reproduction steps in `BUILD.md`.

Changing the plugin/profile interrupts capture. Stop other camera consumers before replacing files. The examples assume that `cam-service`, `imx462-camera`, `imx462-rtsp-server`, and `imx462-health` were all active beforehand; adapt to your own application's service names and original states.

## Verify and back up

Run from the repository root on X5. Preserve the printed backup directory.

```sh
set -eu
python3 scripts/verify_public_release.py
test -f build/libimx462.so
test -f build/imx462_tuning.json
systemctl is-active imx462-health imx462-camera cam-service imx462-rtsp-server
backup_dir="/var/backups/imx462/$(date -u +%Y%m%dT%H%M%SZ)"
sudo install -d -m 0700 "$backup_dir"
sudo cp -a /usr/hobot/lib/sensor/libimx462.so \
  /usr/hobot/lib/sensor/imx462_tuning.json "$backup_dir/"
sudo sh -c 'cd "$1" && sha256sum libimx462.so imx462_tuning.json > SHA256SUMS' sh "$backup_dir"
sudo sh -c 'cd "$1" && sha256sum -c SHA256SUMS' sh "$backup_dir"
printf 'Backup: %s\n' "$backup_dir"
```

If you also change an application binary or service definition, back it up separately. The commands below do not change those files or enable/disable boot services.

## Replace the local files

Stop the recovery supervisor first so it cannot restart capture during replacement. If any command fails, stop and restore both files before starting services.

```sh
set -eu
sudo systemctl stop imx462-health.service
sudo systemctl stop imx462-camera.service
sudo systemctl stop cam-service.service
sudo install -m 0644 build/libimx462.so /usr/hobot/lib/sensor/libimx462.so.new
sudo install -m 0644 build/imx462_tuning.json /usr/hobot/lib/sensor/imx462_tuning.json.new
sudo cmp build/libimx462.so /usr/hobot/lib/sensor/libimx462.so.new
sudo cmp build/imx462_tuning.json /usr/hobot/lib/sensor/imx462_tuning.json.new
sudo mv /usr/hobot/lib/sensor/libimx462.so.new /usr/hobot/lib/sensor/libimx462.so
sudo mv /usr/hobot/lib/sensor/imx462_tuning.json.new /usr/hobot/lib/sensor/imx462_tuning.json
sudo systemctl start cam-service.service
sudo systemctl start imx462-camera.service
sudo systemctl start imx462-health.service
```

Each rename is atomic on the target filesystem; the pair is not a single transaction. An intermediate failure requires restoring both files. Copying these two files does not select the sensor mode in a previously unrelated application.

## Check operation

```sh
systemctl is-active cam-service imx462-camera imx462-rtsp-server imx462-health
systemctl is-enabled cam-service imx462-camera imx462-rtsp-server imx462-health
journalctl -u cam-service -u imx462-camera -u imx462-health --since '5 minutes ago' --no-pager
```

Use your existing RTSP URL, typically `rtsp://<X5_IP>:8554/imx462` in the reference layout, to verify frame progress, 1920 × 1080 geometry, approximately 20 fps, and error logs from a LAN PC. A decoder's frame counter alone does not prove sensor-to-client continuity. Color accuracy requires a separate controlled test.

## Roll back

Set `backup_dir` to the exact saved directory if using a new shell. The commands below assume the original services were active.

```sh
set -eu
test -n "${backup_dir:-}"
sudo sh -c 'cd "$1" && sha256sum -c SHA256SUMS' sh "$backup_dir"
sudo systemctl stop imx462-health.service
sudo systemctl stop imx462-camera.service
sudo systemctl stop cam-service.service
sudo cp -a "$backup_dir/libimx462.so" /usr/hobot/lib/sensor/libimx462.so
sudo cp -a "$backup_dir/imx462_tuning.json" /usr/hobot/lib/sensor/imx462_tuning.json
sudo cmp "$backup_dir/libimx462.so" /usr/hobot/lib/sensor/libimx462.so
sudo cmp "$backup_dir/imx462_tuning.json" /usr/hobot/lib/sensor/imx462_tuning.json
sudo systemctl start cam-service.service
sudo systemctl start imx462-camera.service
sudo systemctl start imx462-health.service
```

Restore any separately modified application/configuration files as well. These manual installation and rollback procedures were not exercised against the live camera during packaging.
