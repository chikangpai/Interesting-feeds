// No image usage; removed to satisfy ESLint

interface FeedItem {
  link: string;
  title: string;
  published: string;
  source: string;
  summary: string;
}

function formatLinkForDisplay(link: string, source: string, baseUrl: string): string {
  // Handle Books specifically - link to Readwise Reader
  if (source === 'Books(local file)') {
    return 'https://read.readwise.io/new';
  }
  
  // Handle other local files - convert API path to full URL
  if (source.includes('(local file)') && link.startsWith('/api/files/')) {
    return `${baseUrl}${link}`;
  }
  return link;
}

export default async function Home() {
  const baseUrl = process.env.FEEDS_API_URL || "http://localhost:8000";
  const endpoint = `${baseUrl}/api/latest`;
  // Log on the server console which endpoint we're hitting
  // and expose it in the UI (dev only) so you can confirm it points to :8000
  console.log("Fetching feed from", endpoint);
  const res = await fetch(endpoint, { cache: "no-store" });
  
  if (!res.ok) {
    return (
      <main className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">CK&apos;s Curated Feed</h1>
        {process.env.NODE_ENV !== "production" && (
          <p className="text-xs text-gray-400 mb-4">Debug: fetching from {endpoint}</p>
        )}
        <p className="text-red-500">Failed to fetch articles. Make sure the backend API is running.</p>
      </main>
    )
  }

  const items: FeedItem[] = await res.json();

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">CK&apos;s Curated Feed</h1>
      {process.env.NODE_ENV !== "production" && (
        <p className="text-xs text-gray-400 mb-4">Debug: fetching from {endpoint}</p>
      )}
      <ul className="space-y-6">
        {items.map((it) => {
          const displayLink = formatLinkForDisplay(it.link, it.source, baseUrl);
          const isLocalFile = it.source.includes('(local file)');
          
          return (
            <li key={it.link} className={`border-l-4 pl-4 ${isLocalFile ? 'border-blue-400 bg-blue-50' : ''}`}>
              <a 
                href={displayLink} 
                className="text-xl font-semibold hover:underline" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                {isLocalFile ? '📄 ' : ''}{it.title}
              </a>
              <p className="text-sm text-gray-500">
                {new Date(it.published).toLocaleString()} — {it.source}
              </p>
              <p>{it.summary}</p>
            </li>
          );
        })}
      </ul>
    </main>
  );
}
