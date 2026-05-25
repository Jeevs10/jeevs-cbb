"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from 'react';
import { TEAM_COLORS } from '@/app/game/teamColors';

interface SimilarPlayer {
  AthleteSourceId: string;
  player_name: string;
  team: string;
  pos: string;
  year: number;
  similarity: number;
  reasons: Array<{
    feature: string;
    delta: number;
  }>;
  differences?: Array<{
    feature: string;
    delta: number;
  }>;
}

interface PlayerSimilarPanelProps {
  player: any;
  similar: { combined: SimilarPlayer[] };
  styleWeight: number;
  setStyleWeight: (value: number) => void;
}

export default function PlayerSimilarPanel({
  player,
  similar,
  styleWeight,
  setStyleWeight,
}: PlayerSimilarPanelProps) {
  const combined = similar?.combined ?? [];
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const shouldStopRef = useRef(false);

  const toggleCardFlip = (cardId: string) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(cardId)) {
        newSet.delete(cardId);
      } else {
        newSet.add(cardId);
      }
      return newSet;
    });
  };

  const getTeamColor = (teamName: string) => {
    return TEAM_COLORS[teamName] || { primary: '#1a1a1a', secondary: '#4a4a4a' };
  };

  // Autoscroll effect
  useEffect(() => {
    if (!scrollContainerRef.current || !isAutoScrolling) return;

    const scrollContainer = scrollContainerRef.current;
    let scrollAmount = scrollContainer.scrollLeft;
    const scrollSpeed = 0.5; // pixels per frame
    let animationId: number;

    const scroll = () => {
      if (shouldStopRef.current) {
        shouldStopRef.current = false;
        setIsAutoScrolling(false);
        return;
      }
      
      if (!isAutoScrolling) return;
      
      scrollAmount += scrollSpeed;
      scrollContainer.scrollLeft = scrollAmount;

      // Reset when reaching the end
      if (scrollContainer.scrollLeft >= scrollContainer.scrollWidth - scrollContainer.clientWidth) {
        scrollAmount = 0;
        scrollContainer.scrollLeft = 0;
      }

      animationId = requestAnimationFrame(scroll);
    };

    animationId = requestAnimationFrame(scroll);

    return () => cancelAnimationFrame(animationId);
  }, [isAutoScrolling, combined.length]);

  // Stop autoscroll on user interaction
  const handleUserInteraction = () => {
    shouldStopRef.current = true;
    setIsAutoScrolling(false);
  };

  // Resume autoscroll after inactivity
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    const resetAutoScroll = () => {
      timeoutId = setTimeout(() => {
        shouldStopRef.current = false;
        setIsAutoScrolling(true);
      }, 3000); // Resume after 3 seconds of inactivity
    };

    if (!isAutoScrolling) {
      resetAutoScroll();
    }

    return () => clearTimeout(timeoutId);
  }, [isAutoScrolling]);

  return (
    <div className="space-y-2">

      {/* SLIDER */}
      <div className="text-[10px] mb-2">
        <div className="font-bold mb-1">Impact ↔ Style Balance</div>

        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={styleWeight}
          onChange={(e) => setStyleWeight(Number(e.target.value))}
          className="w-full"
        />

        <div className="flex justify-between text-[9px] opacity-70">
          <span>Impact</span>
          <span>Style</span>
        </div>
      </div>

      {/* HORIZONTAL SCROLL AREA */}
      <div 
        ref={scrollContainerRef}
        className="flex gap-4 overflow-x-auto pb-4 px-1 scrollbar-thin scrollbar-thumb-black scrollbar-track-gray-200"
        onWheel={handleUserInteraction}
      >

        {/* EMPTY */}
        {combined.length === 0 && (
          <div className="text-xs opacity-70 w-full">
            No similar players found.
          </div>
        )}

        {/* CARDS */}
        {combined.map((p) => {
          const cardId = `similar-${p.AthleteSourceId}`;
          const isFlipped = flippedCards.has(cardId);
          const teamColor = getTeamColor(p.team || '');

          return (
            <div key={p.AthleteSourceId} className="flex-shrink-0">
              <div
                className="card-flip-container w-40 h-52 cursor-pointer"
                onClick={() => {
                  handleUserInteraction();
                  toggleCardFlip(cardId);
                }}
              >
                <div className={`card-flip-inner w-full h-full relative transition-transform duration-500 ${isFlipped ? 'flipped' : ''}`}>

                  {/* Front of card */}
                  <div
                    className="card-flip-front absolute w-full h-full border-3 border-black rounded-lg shadow-[3px_3px_0px_black] overflow-hidden bg-white"
                  >
                    {/* Card header with team primary color */}
                    <div
                      className="text-white p-2 text-center"
                      style={{
                        backgroundColor: teamColor.primary
                      }}
                    >
                      <div className="text-[9px] font-bold tracking-wider truncate">
                        {p.player_name || `${p.AthleteSourceId}`}
                      </div>
                    </div>

                    {/* Player info */}
                    <div className="p-2 flex flex-col items-center text-center bg-white">
                      <div className="text-[8px] text-black mb-1">
                        <span className="font-bold">{p.team || 'No Team'}</span>
                      </div>
                      <div className="text-[8px] text-black/70 mb-1">
                        {p.pos || 'No Position'} • {p.year || 'No Year'}
                      </div>
                      <div className="text-[10px] font-bold text-black mt-2">
                        {((p.similarity ?? 0) * 100).toFixed(1)}%
                      </div>
                      <div className="text-[7px] text-black/50">
                        Similarity
                      </div>
                    </div>

                    {/* Card footer with team secondary color */}
                    <div
                      className="absolute bottom-0 left-0 right-0 h-1.5"
                      style={{
                        backgroundColor: teamColor.secondary
                      }}
                    ></div>
                  </div>

                  {/* Back of card */}
                  <div
                    className="card-flip-back absolute w-full h-full border-3 border-black rounded-lg shadow-[3px_3px_0px_black] overflow-hidden bg-white"
                  >
                    {/* Card header with team primary color */}
                    <div
                      className="text-white p-2 text-center"
                      style={{
                        backgroundColor: teamColor.primary
                      }}
                    >
                      <div className="text-[9px] font-bold tracking-wider">
                        Similarities
                      </div>
                    </div>

                    {/* Similarities and differences */}
                    <div className="p-2 text-[8px] bg-white overflow-y-auto">
                      <div className="mb-2">
                        <div className="font-bold text-black mb-1 text-[7px]">WHY SIMILAR:</div>
                        {p.reasons && p.reasons.length > 0 ? (
                          p.reasons.slice(0, 3).map((r, i) => (
                            <div key={i} className="text-black/80 truncate">• {r.feature}</div>
                          ))
                        ) : (
                          <div className="text-black/60">• stylistic + impact</div>
                        )}
                      </div>

                      <div>
                        <div className="font-bold text-black mb-1 text-[7px]">DIFFERENCES:</div>
                        {p.differences && p.differences.length > 0 ? (
                          p.differences.slice(0, 3).map((d, i) => (
                            <div key={i} className="text-black/80 truncate">• {d.feature}</div>
                          ))
                        ) : (
                          <div className="text-black/60">• minimal differences</div>
                        )}
                      </div>
                    </div>

                    {/* Card footer with team secondary color */}
                    <div
                      className="absolute bottom-0 left-0 right-0 h-1.5"
                      style={{
                        backgroundColor: teamColor.secondary
                      }}
                    ></div>
                  </div>

                </div>
              </div>

              {/* Link to player page */}
              <Link
                href={`/player/${p.AthleteSourceId}`}
                className="block text-center mt-2 text-[9px] font-bold hover:underline"
                onClick={(e) => {
                  e.stopPropagation();
                  handleUserInteraction();
                }}
                onMouseDown={handleUserInteraction}
              >
                View Profile
              </Link>
            </div>
          );
        })}

      </div>
    </div>
  );
}