import Image from "next/image";

export default async function Home() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!apiUrl) {
    return (
      <main className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">CK's Curated Feed</h1>
        <div className="text-red-500 bg-red-100 border border-red-400 rounded p-4">
          <p className="font-bold">Configuration Error</p>
          <p>
            The environment variable <code>NEXT_PUBLIC_API_URL</code> is not set.
          </p>
          <p className="mt-2">
            Please create a file named <code>.env.local</code> in the <code>frontend</code> directory and add the following content:
          </p>
          <pre className="bg-gray-200 text-black p-2 rounded mt-2">
            <code>NEXT_PUBLIC_API_URL=http://127.0.0.1:8000</code>
          </pre>
          <p className="mt-2">After creating the file, you must restart the frontend development server.</p>
        </div>
      </main>
    );
  }

  const res = await fetch(`${apiUrl}/api/latest`,
                          { next: { revalidate: 300 } });
  
  if (!res.ok) {
    return (
      <main className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-4">CK's Curated Feed</h1>
        <p className="text-red-500">Failed to fetch articles. Make sure the backend API is running.</p>
      </main>
    )
  }

  const items = await res.json();

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">CK's Curated Feed</h1>
      <ul className="space-y-6">
        {items.map((it:any) => (
          <li key={it.link} className="border-l-4 pl-4">
            <a href={it.link} className="text-xl font-semibold hover:underline" target="_blank" rel="noopener noreferrer">
              {it.title}
            </a>
            <p className="text-sm text-gray-500">
              {new Date(it.published).toLocaleString()} — {it.source}
            </p>
            <p>{it.summary}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}
