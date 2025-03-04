'use client'; // Needed for client-side animations

import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Image from 'next/image';
import fridgeClosed from '../../public/fridge.png';

export default function Home() {
  const router = useRouter();

  return (
    <div className="flex items-center justify-center h-screen bg-blue-200">
      <motion.div
        className="cursor-pointer flex justify-center items-center"
        whileTap={{ rotateY: 180 }} // Fridge door animation
        transition={{ duration: 0.6 }}
        onClick={() => router.push('/fridge')}
      >
        <Image
          src={fridgeClosed}
          alt="Fridge"
          layout="intrinsic"
          className="max-w-full max-h-full object-contain"
        />
      </motion.div>
    </div>
  );
}
