module.exports = {
  apps: [{
    name: "options-trading",
    cwd: "/Users/ayong/projects/auto-company_test/projects/options_arbitrage_system",
    script: "/Users/ayong/projects/auto-company_test/projects/options_arbitrage_system/.venv/bin/python",
    args: ["web/app.py", "127.0.0.1", "5100"],
    interpreter: "",
    instances: 1,
    exec_mode: "fork",
    autorestart: true,
    watch: false,
    max_memory_restart: "256M",
    env: {
      PYTHONPATH: "/Users/ayong/projects/auto-company_test/projects/options_arbitrage_system",
    },
  }]
};
