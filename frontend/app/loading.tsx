import Logo from '@/components/ui/Logo';

export default function Loading() {
  return (
    <div className="splash">
      <div className="splashLogo">
        <Logo fontSize="clamp(1.15rem, 4vw, 1.6rem)" />
      </div>
      <div className="splashBar" />
    </div>
  );
}
