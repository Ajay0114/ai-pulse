export type DiscoverItem = {
  slug: string;
  name: string;
  description: string;
  icon: string;
  query: string;
  kind: "topic" | "company" | "model";
};

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const RAW_TOPICS = [
  {
    name: "AI Agents",
    description: "Autonomous agents, agentic workflows and orchestration",
    icon: "🤖",
    query: "AI agents",
  },
  {
    name: "Large Language Models",
    description: "LLMs, reasoning models and language technologies",
    icon: "🧠",
    query: "large language models",
  },
  {
    name: "Generative AI",
    description: "Text, image, video and audio generation",
    icon: "✨",
    query: "generative AI",
  },
  {
    name: "AI Coding",
    description: "Coding assistants, AI IDEs and software engineering",
    icon: "💻",
    query: "AI coding",
  },
  {
    name: "Robotics",
    description: "Robotics, physical AI and autonomous systems",
    icon: "🦾",
    query: "AI robotics",
  },
  {
    name: "Machine Learning",
    description: "ML research, algorithms and applications",
    icon: "📊",
    query: "machine learning",
  },
  {
    name: "Computer Vision",
    description: "Image recognition, vision models and multimodal AI",
    icon: "👁️",
    query: "computer vision AI",
  },
  {
    name: "AI Infrastructure",
    description: "GPUs, inference, training and AI infrastructure",
    icon: "⚙️",
    query: "AI infrastructure",
  },
];

const RAW_COMPANIES = [
  { name: "OpenAI", description: "AI models and products" },
  { name: "Google DeepMind", description: "AI research and foundation models" },
  { name: "Anthropic", description: "AI assistants and foundation models" },
  { name: "Meta AI", description: "Open models and AI research" },
  { name: "Microsoft AI", description: "AI platforms and products" },
  { name: "NVIDIA", description: "AI computing and infrastructure" },
  { name: "Hugging Face", description: "Open-source AI ecosystem" },
  { name: "xAI", description: "AI models and research" },
];

const RAW_MODEL_CATEGORIES = [
  { name: "Language Models", query: "language models", icon: "🧠" },
  { name: "AI Coding Tools", query: "AI coding tools", icon: "💻" },
  { name: "Image Generation", query: "AI image generation", icon: "🎨" },
  { name: "Video Generation", query: "AI video generation", icon: "🎬" },
  { name: "Voice & Audio AI", query: "AI voice audio", icon: "🎙️" },
  { name: "AI Development Tools", query: "AI developer tools", icon: "🛠️" },
];

export const DISCOVER_TOPICS: DiscoverItem[] = RAW_TOPICS.map((topic) => ({
  slug: slugify(topic.name),
  name: topic.name,
  description: topic.description,
  icon: topic.icon,
  query: topic.query,
  kind: "topic",
}));

export const DISCOVER_COMPANIES: DiscoverItem[] = RAW_COMPANIES.map(
  (company) => ({
    slug: slugify(company.name),
    name: company.name,
    description: company.description,
    icon: "🏢",
    query: company.name,
    kind: "company",
  })
);

export const DISCOVER_MODEL_CATEGORIES: DiscoverItem[] =
  RAW_MODEL_CATEGORIES.map((category) => ({
    slug: slugify(category.name),
    name: category.name,
    description: `Browse coverage of ${category.name.toLowerCase()}.`,
    icon: category.icon,
    query: category.query,
    kind: "model",
  }));

export const ALL_DISCOVER_ITEMS: DiscoverItem[] = [
  ...DISCOVER_TOPICS,
  ...DISCOVER_COMPANIES,
  ...DISCOVER_MODEL_CATEGORIES,
];

export function getDiscoverItem(slug: string): DiscoverItem | undefined {
  return ALL_DISCOVER_ITEMS.find((item) => item.slug === slug);
}
