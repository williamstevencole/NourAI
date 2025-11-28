import { memo } from 'react';

interface NutriaAvatarProps {
  size?: number;
  className?: string;
}

export const NutriaAvatar = memo(function NutriaAvatar({ size = 40, className = '' }: NutriaAvatarProps) {
  return (
    <img
      src="/nutria.png"
      alt="Logo"
      width={size}
      height={size}
      className={className}
      style={{ objectFit: 'contain', transform: 'translateY(10%)' }}
    />
  );
});
