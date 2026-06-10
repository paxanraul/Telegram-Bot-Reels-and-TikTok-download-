module.exports = {
  apps: [
    {
      name: "video-bot",
      script: "main.py",
      interpreter: "./venv/bin/python",
      cwd: "/opt/video-bot",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};
