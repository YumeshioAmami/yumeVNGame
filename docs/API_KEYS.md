# API Key 创建指南

> 不要把 Key 发到 GitHub、Issue、截图或公开聊天里。  
> yumeVNGame 会把 Key 加密保存在本机 `%APPDATA%\yumeVNGame\secrets.enc`。

设置页现在有 **图片与音乐 API Keys** 面板，可以直接填 fal / Replicate / NovelAI / Stability / ElevenLabs 的 Key。

## 0. NanoGPT（低门槛按量 API）

注册：

<https://nano-gpt.com/>

创建 Key：

1. 登录后打开 API 页面：<https://nano-gpt.com/api>
2. 点击 **Create API key**；
3. 复制 Key；
4. 在 Usage & billing / Pricing 页面充值；
5. 最低可从 **$0.10 加密货币** 或 **$1 银行卡** 开始。

API：

```text
Base URL: https://api.nano-gpt.com/api/v1
Authorization: Bearer YOUR_API_KEY
```

图片模型列表：

```text
GET https://api.nano-gpt.com/api/v1/images/models
```

这个接口会返回每个模型的能力和 `capabilities.nsfw` 标记，可以直接筛选支持 NSFW / image-to-image 的模型。

## 1. fal.ai

注册 / 登录：

<https://fal.ai/>

创建 Key：

1. 登录后打开 Dashboard；
2. 进入 **Keys**：<https://fal.ai/dashboard/keys>
3. 点击 **Add key** / **Create key**；
4. 给 Key 起一个名字，例如 `yumevngame-local`；
5. 复制生成的完整 Key；
6. 在 **Billing** 里绑定支付方式或购买额度：<https://fal.ai/dashboard/billing>

使用方式：

```text
provider: fal
API Key: 你复制的 Key
```

## 2. Replicate

注册 / 登录：

<https://replicate.com/>

创建 Token：

1. 登录后打开 Account；
2. 进入 **API tokens**：<https://replicate.com/account/api-tokens>
3. 点击 **Create token**；
4. 起名，例如 `yumevngame-local`；
5. 复制 token；
6. 在 **Billing** 里绑定支付方式：<https://replicate.com/account/billing>

使用方式：

```text
provider: replicate
API Token: 你复制的 token
```

## 3. NovelAI（可选）

注册 / 订阅：

<https://novelai.net/>

创建 Token：

1. 注册并订阅 Tablet / Scroll / Opus；
2. 打开 Account Settings；
3. 找到 **API Tokens**；
4. 生成一个 persistent token；
5. 复制 token。

注意：

- NovelAI 是订阅制，不是按张计费；
- 从部分网络访问 `novelai.net` 可能超时；
- 拿到 token 后不要提交到仓库。

## 4. 先创建哪一个

建议顺序：

1. **fal.ai**：主图片 API，先创建；
2. **Replicate**：备选模型和 Qwen / Kontext / Seedream，第二创建；
3. **NovelAI**：只有确定需要 NSFW 动漫单图时再订阅。

## 5. Key 放哪里

推荐你自己在应用设置页填入，或者交给我时只写入本机加密存储。

绝对不要：

- 写进 README；
- 写进 `.env` 后提交；
- 发到 GitHub Issue；
- 发到公开聊天截图；
- 写进源码。

当前已有的加密存储：

```text
%APPDATA%\yumeVNGame\secrets.enc
%APPDATA%\yumeVNGame\master.key
```

这两个文件都不在仓库里。

