'use strict';

const express = require('express');
const Anthropic = require('@anthropic-ai/sdk');
const path = require('path');

const app = express();
const client = new Anthropic();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Mock X trending data simulating real trend patterns by category
const TRENDING_DATA = {
  anime: {
    label: 'アニメ・キャラクター',
    hashtags: ['#イラスト', '#キャラクター', '#アニメ', '#fanart', '#二次創作', '#オリジナル'],
    trending: [
      {
        title: '美少女キャラクター立ち絵',
        likes: 45200,
        retweets: 12300,
        description: '淡い色調の美少女キャラクター、白を基調とした清楚な衣装、柔らかい逆光の演出、透明感のある肌表現'
      },
      {
        title: 'RPGファンタジーキャラクター',
        likes: 38700,
        retweets: 9800,
        description: '精緻な鎧を着た戦士キャラクター、動的な攻撃ポーズ、迫力のあるエフェクト、暗い背景とのコントラスト'
      },
      {
        title: '日常系ほのぼのイラスト',
        likes: 52100,
        retweets: 15600,
        description: '学校制服の女の子、放課後のカフェシーン、温かみのあるオレンジ系色彩、自然な表情'
      },
      {
        title: 'ダークファンタジー系魔法使い',
        likes: 29400,
        retweets: 7900,
        description: '暗い配色と紫の魔法エフェクト、ローブを纏った魔法使いキャラクター、神秘的な魔法陣'
      },
      {
        title: '獣耳ケモミミキャラクター',
        likes: 61800,
        retweets: 18400,
        description: '可愛い獣耳、ふわふわした毛並みの質感、パステルカラーの衣装、あどけない表情'
      }
    ]
  },
  landscape: {
    label: '風景・背景',
    hashtags: ['#風景イラスト', '#背景', '#landscape', '#自然', '#都市風景', '#環境アート'],
    trending: [
      {
        title: '夕暮れの街並みシルエット',
        likes: 73200,
        retweets: 22100,
        description: 'オレンジと紫のグラデーション夕焼け空、建物のシルエット、郷愁感のある電柱と電線'
      },
      {
        title: '幻想的な光差し込む森',
        likes: 58400,
        retweets: 16200,
        description: '木漏れ日が差し込む深い森、浮遊する光の粒子、苔むした地面、ファンタジー要素'
      },
      {
        title: '和風桜の庭園',
        likes: 44100,
        retweets: 11700,
        description: '満開の桜の花びら舞い散る庭園、石灯籠、池の水面反射、静寂と美しさ'
      },
      {
        title: '黄金色の海辺の夕日',
        likes: 89300,
        retweets: 27800,
        description: '地平線に沈む夕日、黄金に輝く海面、波の泡が光る、ドラマチックな色彩'
      },
      {
        title: 'ネオン輝くサイバーパンク都市',
        likes: 65700,
        retweets: 19300,
        description: '青とピンクのネオンサイン、雨に濡れた路面反射、霧と高層ビル群、近未来都市'
      }
    ]
  },
  fantasy: {
    label: 'ファンタジー',
    hashtags: ['#fantasy', '#ファンタジー', '#魔法', '#dragon', '#originalart', '#世界観'],
    trending: [
      {
        title: '巨大ドラゴンと騎士の対決',
        likes: 42300,
        retweets: 11200,
        description: '翼を広げた巨大ドラゴン、炎のブレス、立ち向かう騎士、劇的な明暗コントラスト'
      },
      {
        title: '魔法陣を展開する魔法使い',
        likes: 56900,
        retweets: 14700,
        description: '床に展開する複雑な光る魔法陣、ローブを纏った魔法使い、浮遊する魔法書'
      },
      {
        title: '雲上に浮かぶ天空の城',
        likes: 71400,
        retweets: 21600,
        description: '綿雲の上に聳える壮大な城、スチームパンク要素、夕焼け空、飛空挺'
      },
      {
        title: '妖精が住む秘密の森',
        likes: 48200,
        retweets: 13100,
        description: '巨大なきのこ、小さな妖精たち、蛍のような光の粒子、メルヘン的な雰囲気'
      },
      {
        title: 'ジャングルに埋もれた古代神殿',
        likes: 35600,
        retweets: 8700,
        description: '苔生した巨大な石造り神殿、謎めいた古代文字の彫刻、光が差し込む遺跡'
      }
    ]
  },
  portrait: {
    label: 'ポートレート・人物',
    hashtags: ['#ポートレート', '#portrait', '#人物イラスト', '#美人画', '#fashion'],
    trending: [
      {
        title: '艶やかな着物美人',
        likes: 81600,
        retweets: 24300,
        description: '艶やかな花柄着物、日本髪に簪、凛とした横顔、散る桜の花びら'
      },
      {
        title: 'モダンストリートファッション',
        likes: 63200,
        retweets: 18100,
        description: 'おしゃれなストリートファッション、都市的な背景、鮮やかな配色、ポップアート風'
      },
      {
        title: 'ゴシックダークエレガント',
        likes: 55400,
        retweets: 15300,
        description: '黒と深紅の配色、精緻なレース衣装、バラの花、ゴシック建築の背景'
      },
      {
        title: '逆光に包まれる少女',
        likes: 94700,
        retweets: 29600,
        description: '柔らかな逆光、白い夏服ワンピース、穏やかな笑顔、野原と青空'
      },
      {
        title: 'サイバー系戦闘女性キャラ',
        likes: 47100,
        retweets: 13400,
        description: 'クールな表情、高機能な武器、SF・ミリタリー系衣装、廃墟の背景'
      }
    ]
  },
  scifi: {
    label: 'SF・サイバーパンク',
    hashtags: ['#SF', '#cyberpunk', '#scifi', '#未来', '#ロボット', '#mecha'],
    trending: [
      {
        title: 'サイバーパンク少女',
        likes: 77400,
        retweets: 23100,
        description: 'ネオンカラーのサイバネティックアクセサリー、雨のサイバー都市、近未来的衣装'
      },
      {
        title: '精緻なメカニカルロボット',
        likes: 52700,
        retweets: 15800,
        description: '精密な機械部品の描写、金属の質感とハイライト、動的なポーズ、未来的デザイン'
      },
      {
        title: '壮大な宇宙と星雲',
        likes: 68900,
        retweets: 20400,
        description: '広大な宇宙空間、カラフルな星雲と惑星、宇宙船シルエット、スケール感'
      },
      {
        title: '未来都市のパイロット',
        likes: 43600,
        retweets: 12500,
        description: '次世代パイロットスーツ、ホログラムHUD、未来都市コックピット、飛行感'
      },
      {
        title: 'アンドロイド少女',
        likes: 86200,
        retweets: 26700,
        description: '機械と人間の融合デザイン、透明感のある肌に見える機械部品、光る瞳'
      }
    ]
  },
  nature: {
    label: '自然・動物',
    hashtags: ['#自然', '#動物', '#nature', '#animal', '#cute', '#生き物'],
    trending: [
      {
        title: '可愛い猫のほのぼのイラスト',
        likes: 112000,
        retweets: 34500,
        description: 'もふもふした猫、日差しの中でくつろぐ姿、パステルカラー、癒し系'
      },
      {
        title: '幻想的な蝶の群れ',
        likes: 67300,
        retweets: 19800,
        description: 'カラフルな蝶が舞う、光の粒子、花畑の背景、夢幻的な雰囲気'
      },
      {
        title: '雪原のオオカミ',
        likes: 54800,
        retweets: 16100,
        description: '雪を踏むオオカミ、息の白い煙、静寂な冬の森、月明かり'
      },
      {
        title: '海底の幻想的な世界',
        likes: 79200,
        retweets: 23600,
        description: '色鮮やかな珊瑚礁、熱帯魚の群れ、光が差し込む海中、神秘的な青'
      },
      {
        title: '桜と小鳥',
        likes: 88400,
        retweets: 27200,
        description: '満開の桜枝に止まる小鳥、花びらが舞う、柔らかい春の光、和の情緒'
      }
    ]
  }
};

// POST /api/analyze - analyze X trends with Claude and generate image prompts
app.post('/api/analyze', async (req, res) => {
  const { category, customKeywords } = req.body;

  const trendData = TRENDING_DATA[category];
  if (!trendData && !customKeywords) {
    return res.status(400).json({ error: 'カテゴリーまたはキーワードを指定してください' });
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    let contextData = '';

    if (trendData) {
      const sorted = [...trendData.trending].sort((a, b) => (b.likes + b.retweets * 2) - (a.likes + a.retweets * 2));
      contextData = `
カテゴリー: ${trendData.label}
人気ハッシュタグ: ${trendData.hashtags.join(', ')}

人気コンテンツランキング（エンゲージメント順）:
${sorted.map((t, i) => `
${i + 1}位. 「${t.title}」
   いいね数: ${t.likes.toLocaleString()} | RT数: ${t.retweets.toLocaleString()}
   視覚的特徴: ${t.description}`).join('\n')}
`;
    }

    if (customKeywords) {
      contextData += `\nユーザー指定の追加キーワード・テーマ: ${customKeywords}`;
    }

    const systemPrompt = `あなたはSNSビジュアルコンテンツのトレンド分析専門家であり、AIイラスト生成プロンプトエンジニアです。
X(旧Twitter)の人気イラストデータを分析し、なぜそのコンテンツが多くのエンゲージメントを獲得したかを解析します。
そして、同様の人気を得られる可能性の高い画像生成AIプロンプトを作成します。

プロンプトはStable Diffusion、Midjourney、DALL-E等で使える詳細な英語プロンプトを生成してください。`;

    const userMessage = `以下のXのトレンドデータを分析し、人気イラストの傾向と画像生成プロンプトを生成してください。

${contextData}

以下のJSON形式で回答してください（JSONのみ、説明文は不要）:

{
  "analysis": {
    "summary": "トレンドの全体的な傾向と人気の理由（150〜200字）",
    "popularElements": ["人気要素1", "人気要素2", "人気要素3", "人気要素4", "人気要素5"],
    "colorTrends": ["色彩傾向1", "色彩傾向2", "色彩傾向3"],
    "compositionTips": ["構図ポイント1", "構図ポイント2", "構図ポイント3"],
    "engagementFactors": ["高エンゲージメント要因1", "高エンゲージメント要因2", "高エンゲージメント要因3"]
  },
  "prompts": [
    {
      "title": "プロンプト1のタイトル（日本語）",
      "theme": "テーマの説明（日本語、50字程度）",
      "positive": "1girl, detailed anime art, masterpiece, best quality, [具体的で詳細な英語プロンプト]",
      "negative": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
      "tips": "このプロンプトの活用ヒント（日本語）"
    },
    {
      "title": "プロンプト2のタイトル（日本語）",
      "theme": "テーマの説明（日本語、50字程度）",
      "positive": "詳細な英語プロンプト",
      "negative": "英語のネガティブプロンプト",
      "tips": "このプロンプトの活用ヒント（日本語）"
    },
    {
      "title": "プロンプト3のタイトル（日本語）",
      "theme": "テーマの説明（日本語、50字程度）",
      "positive": "詳細な英語プロンプト",
      "negative": "英語のネガティブプロンプト",
      "tips": "このプロンプトの活用ヒント（日本語）"
    }
  ]
}`;

    const stream = client.messages.stream({
      model: 'claude-opus-4-6',
      max_tokens: 4000,
      thinking: { type: 'adaptive' },
      system: systemPrompt,
      messages: [{ role: 'user', content: userMessage }]
    });

    let fullText = '';

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        fullText += event.delta.text;
        res.write(`data: ${JSON.stringify({ type: 'chunk', text: event.delta.text })}\n\n`);
      }
    }

    // Parse and send structured result
    try {
      const jsonMatch = fullText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        res.write(`data: ${JSON.stringify({ type: 'complete', data: parsed })}\n\n`);
      } else {
        res.write(`data: ${JSON.stringify({ type: 'error', message: 'レスポンスのパースに失敗しました' })}\n\n`);
      }
    } catch (parseError) {
      res.write(`data: ${JSON.stringify({ type: 'error', message: 'JSONパースエラー: ' + parseError.message })}\n\n`);
    }

    res.write('data: [DONE]\n\n');
    res.end();
  } catch (error) {
    res.write(`data: ${JSON.stringify({ type: 'error', message: error.message })}\n\n`);
    res.write('data: [DONE]\n\n');
    res.end();
  }
});

// GET /api/categories - return available categories
app.get('/api/categories', (req, res) => {
  const categories = Object.entries(TRENDING_DATA).map(([key, val]) => ({
    key,
    label: val.label,
    hashtags: val.hashtags.slice(0, 3),
    topLikes: Math.max(...val.trending.map(t => t.likes)).toLocaleString()
  }));
  res.json(categories);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 X トレンド分析サーバー起動中: http://localhost:${PORT}`);
});
