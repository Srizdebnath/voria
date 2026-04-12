import fs from 'fs';
import path from 'path';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Link from 'next/link';
import { notFound } from 'next/navigation';

export default async function DocPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const docsDir = path.join(process.cwd(), '../docs');
  const filePath = path.join(docsDir, `${slug}.md`);

  if (!fs.existsSync(filePath)) {
    return notFound();
  }

  const content = fs.readFileSync(filePath, 'utf8');

  return (
    <div className="container mx-auto px-4 py-12 max-w-5xl">
      <div className="mb-12 flex items-center justify-between">
        <Link href="/" className="brutal-btn flex items-center gap-2 group">
          <span className="group-hover:-translate-x-1 transition-transform">←</span> BACK TO HOME
        </Link>
        <div className="font-black text-2xl uppercase tracking-tighter opacity-20 select-none">
          Voria Internal Documentation
        </div>
      </div>
      
      <div className="brutal-box p-4 md:p-12 bg-[#fffdd0] relative overflow-hidden">
        {/* Subtle grid pattern for the box background */}
        <div className="absolute inset-0 opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '20px 20px' }}></div>
        
        <article className="relative">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({node, ...props}) => <h1 className="text-5xl md:text-7xl font-black mb-10 pb-6 border-b-8 border-black uppercase tracking-tighter leading-none" {...props} />,
              h2: ({node, ...props}) => <h2 className="text-3xl md:text-4xl font-black mt-16 mb-6 uppercase tracking-tight bg-black text-white inline-block px-4 py-2" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-2xl font-bold mt-10 mb-4 border-l-8 border-emerald-400 pl-4" {...props} />,
              p: ({node, ...props}) => <p className="text-xl leading-relaxed mb-6 font-medium text-gray-900" {...props} />,
              ul: ({node, ...props}) => <ul className="list-none mb-8 space-y-4" {...props} />,
              li: ({node, ...props}) => (
                <li className="flex gap-3 text-xl">
                  <span className="text-emerald-500 font-bold shrink-0">▶</span>
                  <span {...props} />
                </li>
              ),
              code: ({node, inline, className, children, ...props}: any) => {
                const match = /language-(\w+)/.exec(className || '')
                return !inline ? (
                  <div className="terminal-window my-8 shadow-2xl">
                    <div className="terminal-header flex items-center px-4 py-2 border-b-2 border-black" style={{ background: '#2d2d30' }}>
                      <div className="flex gap-2">
                        <span className="w-3 h-3 rounded-full bg-[#ff5f56]"></span>
                        <span className="w-3 h-3 rounded-full bg-[#ffbd2e]"></span>
                        <span className="w-3 h-3 rounded-full bg-[#27c93f]"></span>
                      </div>
                      <div className="flex-1 text-center text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                        {match ? match[1] : 'terminal'}
                      </div>
                    </div>
                    <pre className="p-6 overflow-x-auto bg-[#1a1a2e] text-emerald-400 font-mono text-sm leading-relaxed">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  </div>
                ) : (
                  <code className="bg-black text-emerald-400 px-2 py-0.5 rounded font-bold text-base" {...props}>
                    {children}
                  </code>
                )
              },
              a: ({node, ...props}) => <a className="text-emerald-600 font-black underline decoration-4 underline-offset-4 hover:bg-emerald-400 hover:text-black transition-colors" {...props} />,
              blockquote: ({node, ...props}) => <blockquote className="border-4 border-black border-l-[16px] p-6 mb-8 bg-emerald-50 font-bold italic text-2xl" {...props} />,
              hr: () => <hr className="my-16 border-t-8 border-black border-dashed opacity-10" />,
            }}
          >
            {content}
          </ReactMarkdown>
        </article>
      </div>
    </div>
  );
}
