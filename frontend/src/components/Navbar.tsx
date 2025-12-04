
'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { FiSearch, FiMenu } from 'react-icons/fi'

export default function Navbar() {
    return (
        <motion.nav
            className="fixed top-0 z-50 w-full border-b border-[var(--glass-border)] bg-[var(--bg-primary)]/80 backdrop-blur-xl"
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[var(--accent-gold)] to-[var(--accent-gold-dim)]" />
                    <span className="text-xl font-bold tracking-tight text-white">
                        TunisHome <span className="text-[var(--accent-gold)]">Pro</span>
                    </span>
                </Link>

                {/* Desktop Nav */}
                <div className="hidden items-center gap-8 md:flex">
                    <Link href="/buy" className="text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors">
                        Buy
                    </Link>
                    <Link href="/rent" className="text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors">
                        Rent
                    </Link>
                    <Link href="/ai-valuation" className="text-sm font-medium text-[var(--text-secondary)] hover:text-white transition-colors">
                        AI Valuation
                    </Link>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4">
                    <button className="hidden items-center gap-2 rounded-full border border-[var(--glass-border)] bg-[var(--glass-bg)] px-4 py-1.5 text-sm text-[var(--text-secondary)] transition-colors hover:border-[var(--text-secondary)] hover:text-white md:flex">
                        <FiSearch size={14} />
                        <span>Search...</span>
                        <kbd className="ml-2 rounded bg-[var(--bg-tertiary)] px-1.5 py-0.5 text-[10px] font-bold text-[var(--text-tertiary)]">⌘K</kbd>
                    </button>

                    <button className="btn btn-primary text-sm">
                        Sign In
                    </button>

                    <button className="md:hidden text-white">
                        <FiMenu size={24} />
                    </button>
                </div>
            </div>
        </motion.nav>
    )
}
