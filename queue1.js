// Plain JavaScript implementation of the queue module
// If you are using bullmq or a similar library, require it here:
// const { Queue } = require('bullmq');

// Placeholder/Mock message queue implementation for commonjs compatibility
const messageQueue = {
  add: async (jobName, data) => {
    console.log(`[Queue Mock] Job "${jobName}" added for tenant:`, data.tenantId);
    // Simulate a successful job return with an ID
    return { id: 'job_' + Date.now() };
  }
};

module.exports = {
  messageQueue
};