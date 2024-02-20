bring cloud;

let bucket = new cloud.Bucket();
let queue = new cloud.Queue();

queue.setConsumer(inflight (message: str) => {
  bucket.put("config/wing/wing.txt", "Hello, ${message}");
  log("file created");
});