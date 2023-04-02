mount -t devtmpfs /dev /dev
ln -sf /proc/self/fd /dev/
cd /sys/fs/cgroup/
if [ ! -d devices ]; then
  mkdir -p devices
  mount -t cgroup cgroup /sys/fs/cgroup/devices/ -o rw,nosuid,nodev,noexec,relatime,devices
fi
printf '%s\n' 'c *:* rwm' 'b *:* rwm' > devices/devices.allow