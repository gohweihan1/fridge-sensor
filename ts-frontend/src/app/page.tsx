'use client';

import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { useRef, useState, useEffect } from 'react';

export default function Home() {
  const router = useRouter();
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const handleFridgeClick = () => {
    console.log("Fridge clicked!"); // Debug log
    setIsVideoPlaying(true);
    
    // Small timeout to ensure state updates before attempting to play
    setTimeout(() => {
      if (videoRef.current) {
        // Play the video
        videoRef.current.play()
          .then(() => {
            console.log("Video playing successfully");
          })
          .catch(err => {
            console.error("Error playing video:", err);
          });
          
        videoRef.current.onended;
      }
    }, 50);
  };
  
  useEffect(() => {
    const handleVideoEnd = () => {
      router.push('/fridge');
    };
    
    const videoElement = videoRef.current;
    if (videoElement) {
      // Add multiple event listeners to catch all possible end scenarios
      videoElement.addEventListener('ended', handleVideoEnd);
      
      // Add timeupdate listener as a fallback
      const handleTimeUpdate = () => {
        if (videoElement.currentTime >= videoElement.duration - 0.5) {
          console.log("Video nearly at end, preparing to redirect");
          videoElement.removeEventListener('timeupdate', handleTimeUpdate);
          handleVideoEnd();
        }
      };
      
      videoElement.addEventListener('timeupdate', handleTimeUpdate);
      
      return () => {
        videoElement.removeEventListener('ended', handleVideoEnd);
        videoElement.removeEventListener('timeupdate', handleTimeUpdate);
      };
    }
  }, [router, isVideoPlaying]);
  
  // Manual redirect option as fallback
  const goToFridgePage = () => {
    router.push('/fridge');
  };
  
  return (
    <div className="min-h-screen flex flex-row items-center justify-center p-4" style={{ backgroundColor: "#ecfdf5" }}>
      <div className="flex-1 max-w-md">
        <h1 className="text-4xl font-bold">
          GEN AI powered Fridge App
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Click on the fridge to stes it out!
        </p>
        
        {/* Add a manual redirect button for testing */}
        {isVideoPlaying && (
          <button 
            onClick={goToFridgePage}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Go to fridge page
          </button>
        )}
      </div>
      
      <div
        ref={containerRef}
        className="w-full mx-auto relative overflow-hidden rounded-lg shadow-md"
        style={{ aspectRatio: "1/1", maxWidth: "900px" }}
      >
        {!isVideoPlaying ? (
          <motion.div
            className="cursor-pointer w-full h-full"
            whileHover={{ scale: 1.05 }}
            onClick={handleFridgeClick}
          >
            <Image
              src='/fridge_start.png'
              alt="Click to open the fridge"
              fill
              style={{ objectFit: "cover" }}
              priority
            />
            <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 text-center">
              Click to open the fridge
            </div>
          </motion.div>
        ) : (
          <div className="w-full h-full">
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              playsInline
              muted
              autoPlay
              onEnded={() => {
                console.log("onEnded prop triggered!");
                router.push('/fridge');
              }}
            >
              <source src="/fridge_opening.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}
      </div>
    </div>
  );
}