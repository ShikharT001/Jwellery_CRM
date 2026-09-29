import { Inter, Outfit } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/lib/auth/authContext';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata = {
  title: 'Jewellery ERP | Premium SaaS Platform',
  description: 'Premium enterprise resource planning for jewellery businesses',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`} suppressHydrationWarning>
      <body className="min-h-screen flex flex-col">
        <AuthProvider>
          {children}
          <Toaster 
            position="top-right" 
            toastOptions={{
              className: '!bg-navy-surface !text-white !border !border-white/10',
              style: {
                background: '#0F172A',
                color: '#fff',
                border: '1px solid rgba(255,255,255,0.1)',
                backdropFilter: 'blur(10px)'
              },
            }} 
          />
        </AuthProvider>
      </body>
    </html>
  );
}
