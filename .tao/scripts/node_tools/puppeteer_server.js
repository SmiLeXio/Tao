const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const puppeteer = require("puppeteer");

const server = new Server(
  {
    name: "tao-puppeteer",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

let browser;

async function getBrowser() {
  if (!browser) {
    browser = await puppeteer.launch({
      headless: "new",
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });
  }
  return browser;
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "web_screenshot",
        description: "对指定 URL 的网页进行截图并返回 base64",
        inputSchema: {
          type: "object",
          properties: {
            url: { type: "string", description: "要截图的网页 URL" },
            fullPage: { type: "boolean", description: "是否截取全屏", default: false }
          },
          required: ["url"],
        },
      },
      {
        name: "web_content",
        description: "获取指定 URL 网页的完整内容或链接列表",
        inputSchema: {
          type: "object",
          properties: {
            url: { type: "string", description: "网页 URL" },
            mode: { type: "string", enum: ["html", "text", "links"], default: "text" }
          },
          required: ["url"],
        },
      }
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const b = await getBrowser();
  const page = await b.newPage();

  try {
    if (name === "web_screenshot") {
      await page.goto(args.url, { waitUntil: "networkidle2" });
      const screenshot = await page.screenshot({
        encoding: "base64",
        fullPage: args.fullPage || false
      });
      return {
        content: [{ type: "text", text: `截图成功，Base64 长度: ${screenshot.length}` }],
      };
    } else if (name === "web_content") {
      await page.goto(args.url, { waitUntil: "networkidle2" });

      // 模拟滚动以触发懒加载
      await page.evaluate(async () => {
        await new Promise((resolve) => {
          let totalHeight = 0;
          let distance = 100;
          let timer = setInterval(() => {
            let scrollHeight = document.body.scrollHeight;
            window.scrollBy(0, distance);
            totalHeight += distance;
            if (totalHeight >= scrollHeight) {
              clearInterval(timer);
              resolve();
            }
          }, 100);
        });
      });

      let content;
      if (args.mode === "html") {
        content = await page.content();
      } else if (args.mode === "links") {
        content = await page.evaluate(() => {
          const links = Array.from(document.querySelectorAll('a'));
          return links.map(link => ({
            text: link.innerText.trim(),
            href: link.href
          })).filter(l => l.text && l.href.startsWith('http'));
        });
        return {
          content: [{ type: "text", text: JSON.stringify(content, null, 2) }],
        };
      } else {
        content = await page.evaluate(() => document.body.innerText);
      }
      return {
        content: [{ type: "text", text: content.substring(0, 50000) }], // 扩大限制到 50000 字符
      };
    }
  } catch (error) {
    return {
      content: [{ type: "text", text: `错误: ${error.message}` }],
      isError: true,
    };
  } finally {
    await page.close();
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Tao Puppeteer MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
