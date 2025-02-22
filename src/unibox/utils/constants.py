"""commonly used constant variables"""

__all_imgs_raw = "jpg jpeg png bmp dds exif jp2 jpx pcx pnm ras gif tga tif tiff xbm xpm webp jpe"
IMG_FILES = ["." + i.strip() for i in __all_imgs_raw.split(" ")]

# new name
IMAGE_FILES = IMG_FILES

__all_videos_raw = "webm mkv flv vob ogv ogg avi mov qt wmv yuv rm rmvb asf m4v mpeg mp4 mpe mpg m2v 3gp 3g2"
VIDEO_FILES = ["." + i.strip() for i in __all_videos_raw.split(" ")]

__all_audio_raw = "mp3 wav aac flac ogg wma m4a aiff au opus alac amr ac3"
AUDIO_FILES = ["." + i.strip() for i in __all_audio_raw.split(" ")]

# Blacklisted directories and files for uploads to prevent injections
BLACKLISTED_PATHS = {
    "/etc/passwd",   # System user accounts
    "/etc/shadow",   # Encrypted passwords
    "/etc/group",    # User groups
    "/etc/gshadow",  # Group passwords
    "/root/.ssh/",   # SSH keys (entire folder)
    "/root/.bashrc",
    "/root/.profile",
    "/root/.bash_history",  # Bash history (could contain sensitive commands)
    "/root/.viminfo",       # Vim history (could contain credentials)
    
    # System binaries & libraries
    "/bin",
    "/usr/bin",
    "/sbin",
    "/usr/sbin",
    "/lib",
    "/usr/lib",
    "/lib64",
    "/usr/lib64",

    # Boot & system directories
    "/boot",
    "/dev",
    "/proc",
    "/sys",

    # Kernel & logs
    "/var/log",  # Logs (e.g., auth logs, security logs)
    "/var/run",  # PID files and UNIX domain sockets
    "/var/tmp",  # Persistent temp files (attackers sometimes abuse this)
    "/tmp",      # Temporary storage (some exploits target this)

    # Docker & container paths
    "/var/lib/docker",  # Docker container storage
    "/var/lib/lxc",     # LXC container storage
    "/var/lib/kubelet", # Kubernetes node storage

    # SSH, keys, and auth data
    "/etc/ssh/",       # SSH configuration and keys
    "/etc/ssl/",       # SSL/TLS keys and certs
    "/etc/pki/",       # SSL/TLS certs (RedHat-based systems)

    # Systemd and cron jobs
    "/etc/systemd/",    # Systemd services (modification could allow privilege escalation)
    "/etc/init.d/",     # Init scripts (old systems)
    "/etc/cron.d/",     # Scheduled cron jobs
    "/etc/cron.daily/",
    "/etc/cron.hourly/",
    "/etc/cron.monthly/",
    "/etc/cron.weekly/",

    # User & home directories (optional, but can be sensitive)
    "/home/",           # User home directories
    "/var/mail",        # Email storage
    "/var/spool/",      # Printing and mail spool

    # Other credential files: huggingface, AWS, GCP, etc.
    "/root/.huggingface/",
    "/root/.aws/",
    "/root/.gcp/",
    "/root/.azure/",
    "/root/.docker/",
    "/root/.kube/",
}
