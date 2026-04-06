# Tech Stack - BrandCraft

## Document Rendering

| Technology | Version | Function |
|------------|---------|----------|
| Puppeteer | ^23.0 | Headless Chrome → PDF/PNG |
| marked | ^15.0 | Markdown → semantic HTML |
| PptxGenJS | ^3.12 | Native PPTX generation |
| pdf-parse | ^1.1 | PDF reading and extraction |
| pdf-lib | ^1.17 | Advanced PDF manipulation |
| gray-matter | ^4.0 | YAML template parsing |
| cheerio | ^1.0 | HTML token extraction |

## Video Composition

| Technology | Version | Function |
|------------|---------|----------|
| Remotion | ^4.0 | React → Video framework |
| @remotion/cli | ^4.0 | CLI rendering |
| @remotion/bundler | ^4.0 | Webpack bundler |
| @remotion/google-fonts | ^4.0 | Font loading |
| React | ^19.0 | Component runtime |
| TypeScript | ^5.0 | Type safety |

## Image Generation (MCP)

| MCP | Model | Priority | Specialty |
|-----|-------|----------|-----------|
| nano-banana-pro | Google Gemini | 1 (Default) | General generation |
| dalle3 | GPT Image 1.5 | 2 (Fallback) | Photographic quality |
| fal-video | Imagen4, Ideogram | 3 (Alternative) | Photorealism |
| flux | FLUX Kontext Pro | 4 (Specialized) | Maximum prompt adherence |
