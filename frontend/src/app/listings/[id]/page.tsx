
'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { motion } from 'framer-motion'
import { FiMapPin, FiStar, FiHome, FiCalendar, FiMaximize, FiArrowLeft } from 'react-icons/fi'
import Link from 'next/link'
import Image from 'next/image'

export default function ListingPage() {
    const { id } = useParams()
    const [listing, setListing] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchListing() {
            if (!id) return

            if (!supabase) {
                console.warn('Supabase client not initialized')
                setLoading(false)
                return
            }

            try {
                const { data, error } = await supabase
                    .from('listings')
                    .select('*')
                    .eq('id', id)
                    .single()

                if (error) {
                    console.error('Error fetching listing:', error)
                } else {
                    setListing(data)
                }
            } catch (err) {
                console.error('Unexpected error:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchListing()
    }, [id])

    if (loading) {
        return (
            <div className="container py-8">
                <div className="h-96 w-full animate-pulse rounded-xl bg-[var(--glass-bg)]" />
            </div>
        )
    }

    if (!listing) {
        return (
            <div className="container py-8 text-center">
                <h1 className="h2 mb-4">Listing Not Found</h1>
                <Link href="/" className="btn btn-outline">
                    <FiArrowLeft size={16} className="mr-2" />
                    Back to Listings
                </Link>
            </div>
        )
    }

    const formattedPrice = new Intl.NumberFormat('fr-TN', {
        style: 'decimal',
        maximumFractionDigits: 0,
    }).format(listing.price)

    return (
        <div className="container py-8">
            {/* Breadcrumb */}
            <Link href="/" className="mb-6 inline-flex items-center text-sm text-[var(--text-secondary)] hover:text-white">
                <FiArrowLeft size={14} className="mr-1" />
                Back to Listings
            </Link>

            <div className="grid gap-8 lg:grid-cols-2">
                {/* Left Column: Images & Key Info */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    {/* Main Image */}
                    <div className="relative mb-6 aspect-video w-full overflow-hidden rounded-xl bg-neutral-900 border border-[var(--glass-border)]">
                        {listing.image_url ? (
                            <Image
                                src={listing.image_url}
                                alt={listing.title}
                                fill
                                className="object-cover"
                                priority
                            />
                        ) : (
                            <div className="flex h-full w-full items-center justify-center text-neutral-700">
                                <FiHome size={64} />
                            </div>
                        )}

                        {listing.renovation_score !== undefined && (
                            <div className="absolute right-4 top-4">
                                <div className={`badge ${listing.renovation_score >= 7 ? 'badge-emerald' : 'badge-gold'} backdrop-blur-md text-sm py-1 px-3`}>
                                    <FiStar size={14} className="mr-1" />
                                    AI Score: {listing.renovation_score}/10
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Key Stats Grid */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="glass-card p-4 text-center">
                            <div className="mb-1 text-xs text-[var(--text-secondary)]">Price</div>
                            <div className="text-lg font-bold text-[var(--accent-gold)]">{formattedPrice} DT</div>
                        </div>
                        <div className="glass-card p-4 text-center">
                            <div className="mb-1 text-xs text-[var(--text-secondary)]">Rooms</div>
                            <div className="text-lg font-bold">{listing.rooms || '-'}</div>
                        </div>
                        <div className="glass-card p-4 text-center">
                            <div className="mb-1 text-xs text-[var(--text-secondary)]">Area</div>
                            <div className="text-lg font-bold">{listing.area ? `${listing.area} m²` : '-'}</div>
                        </div>
                    </div>
                </motion.div>

                {/* Right Column: Details & Map */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                >
                    <h1 className="h2 mb-2 text-white">{listing.title}</h1>

                    <div className="mb-6 flex items-center text-[var(--text-secondary)]">
                        <FiMapPin size={16} className="mr-2 text-[var(--accent-blue)]" />
                        <span>{listing.location_text}</span>
                    </div>

                    <div className="glass-card mb-8 p-6">
                        <h3 className="h3 mb-4">Description</h3>
                        <p className="text-body whitespace-pre-line">{listing.description || 'No description available.'}</p>
                    </div>

                    {/* Map Placeholder */}
                    <div className="glass-card relative h-64 w-full overflow-hidden bg-neutral-900 p-6">
                        <div className="absolute inset-0 flex items-center justify-center bg-[url('/map-pattern.png')] bg-cover opacity-20">
                            {/* Pattern placeholder */}
                        </div>
                        <div className="relative z-10 flex h-full flex-col items-center justify-center text-center">
                            <FiMapPin size={32} className="mb-2 text-[var(--accent-blue)]" />
                            <h4 className="font-semibold text-white">Map View</h4>
                            <p className="text-sm text-[var(--text-secondary)]">Interactive map coming in Phase 2</p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    )
}
