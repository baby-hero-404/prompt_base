// Deliberate config-singleton anti-pattern
let instance = null;

class Config {
  constructor() {
    if (instance) {
      return instance;
    }
    this.settings = {
      env: process.env.NODE_ENV || 'development',
      port: process.env.PORT || 3000
    };
    instance = this;
  }

  get(key) {
    return this.settings[key];
  }

  set(key, value) {
    this.settings[key] = value;
  }
}

module.exports = new Config();
