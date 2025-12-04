
'use client'

import { motion } from 'framer-motion'
import { FiMapPin, FiStar, FiTrendingUp, FiHome } from 'react-icons/fi'
import Image from 'next/image'
import Link from 'next/link'

interface ListingProps {
    id: string
    title: string
    price: number
    location_text: string
    image_url?: string
    renovation_score?: number
    rooms?: number
    area?: number
}

export default function ListingCard({ listing }: { listing: ListingProps }) {
    const { id, title, price, location_text, image_url, renovation_score, rooms, area } = listing

    // Format price (e.g. 1 200 DT)
    const formattedPrice = new Intl.NumberFormat('fr-TN', {
        style: 'decimal',
        maximumFractionDigits: 0,
    }).format(price)

    return (
        <Link href={`/listings/${id}`}>
            <motion.div
                className="glass-card group relative h-full cursor-pointer overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
            >
                {/* Image Section */}
                <div className="relative aspect-[4/3] w-full overflow-hidden bg-neutral-900">
                    {image_url ? (
                        <Image
                            src={image_url}
                            alt={title}
                            fill
                            className="object-cover transition-transform duration-500 group-hover:scale-110"
                            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        />
                    ) : (
                        <div className="flex h-full w-full items-center justify-center text-neutral-700">
                            <FiHome size={48} />
                        </div>
                    )}

                    {/* AI Score Badge */}
                    {renovation_score !== undefined && (
                        <div className="absolute right-3 top-3 z-10">
                            <div className={`badge ${renovation_score >= 7 ? 'badge-emerald' : 'badge-gold'} backdrop-blur-md`}>
                                <FiStar size={12} className="mr-1" />
                                AI Score: {renovation_score}/10
                            </div>
                        </div>
                    )}

                    {/* Price Overlay */}
                    <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/80 to-transparent p-4 pt-12">
                        <div className="text-xl font-bold text-white">{formattedPrice} DT</div>
                    </div>
                </div>

                {/* Content Section */}
                <div className="p-4">
                    <h3 className="mb-2 line-clamp-1 text-lg font-semibold text-white group-hover:text-[var(--accent-gold)] transition-colors">
                        {title}
                    </h3>

                    <div className="mb-4 flex items-center text-sm text-[var(--text-secondary)]">
                        <FiMapPin size={14} className="mr-1 text-[var(--accent-blue)]" />
                        <span className="line-clamp-1">{location_text}</span>
                    </div>

                    <div className="flex items-center justify-between border-t border-[var(--glass-border)] pt-3 text-xs text-[var(--text-tertiary)]">
                        <div className="flex gap-3">
                            {rooms && <span>{rooms} Beds</span>}
                            {area && <span>{area} m²</span>}
                        </div>
                        <div className="flex items-center text-[var(--accent-emerald)]">
                            <FiTrendingUp size={12} className="mr-1" />
                            <span>Investment Grade</span>
                        </div>
                    </div>
                </div>
            </motion.div>
        </Link>
    )
}
