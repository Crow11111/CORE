const net = require("net");
const [host, port] = process.argv.slice(2);
const client = net.createConnection({ host, port }, () => {
  process.stdin.pipe(client);
  client.pipe(process.stdout);
});
client.on("error", (err) => {
  console.error(err);
  process.exit(1);
});
