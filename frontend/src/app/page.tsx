
'use client'

import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import ListingCard from '@/components/ListingCard'
import { motion } from 'framer-motion'

export default function Home() {
  const [listings, setListings] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchListings() {
      if (!supabase) {
        console.warn('Supabase client not initialized')
        setLoading(false)
        return
      }

      try {
        const { data, error } = await supabase
          .from('listings')
          .select('*')
          .limit(50)

        if (error) {
          console.error('Error fetching listings:', error)
        } else {
          setListings(data || [])
        }
      } catch (err) {
        console.error('Unexpected error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchListings()
  }, [])

  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="h2 mb-2 text-white">Latest Opportunities</h1>
        <p className="text-body">Discover investment-grade properties in Tunisia.</p>
      </div>

      {loading ? (
        <div className="grid-layout">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass-card h-[400px] animate-pulse bg-[var(--glass-bg)]" />
          ))}
        </div>
      ) : listings.length > 0 ? (
        <div className="grid-layout">
          {listings.map((listing) => (
            <motion.div
              key={listing.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <ListingCard listing={listing} />
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-dashed border-[var(--glass-border)] text-[var(--text-secondary)]">
          <p>No listings found.</p>
        </div>
      )}
    </div>
  )
}
