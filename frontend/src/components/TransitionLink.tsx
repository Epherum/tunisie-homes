"use client";

import { useTransitionRouter } from "next-view-transitions";
import Link, { type LinkProps } from "next/link";
import { usePathname } from "next/navigation";
import type { PropsWithChildren } from "react";

function pageAnimate() {
  document.documentElement.animate(
    [
      { opacity: 1, transform: "translateX(0)" },
      { opacity: 0, transform: "translateX(-50px)" },
    ],
    {
      duration: 400,
      easing: "cubic-bezier(0.4, 0.0, 0.2, 1)",
      fill: "forwards",
      pseudoElement: "::view-transition-old(root)",
    },
  );

  document.documentElement.animate(
    [
      { opacity: 0, transform: "translateX(50px)" },
      { opacity: 1, transform: "translateX(0)" },
    ],
    {
      duration: 400,
      easing: "cubic-bezier(0.4, 0.0, 0.2, 1)",
      fill: "forwards",
      pseudoElement: "::view-transition-new(root)",
    },
  );
}

interface TransitionLinkProps extends LinkProps {
  onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
  className?: string;
}

export default function TransitionLink({
  children,
  href,
  onClick,
  ...props
}: PropsWithChildren<TransitionLinkProps>) {
  const router = useTransitionRouter();
  const pathname = usePathname();

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (onClick) {
      onClick(e);
    }

    e.preventDefault();

    if (href.toString() === pathname) {
      return;
    }

    router.push(href.toString(), { onTransitionReady: pageAnimate });
  };

  return (
    <Link href={href} {...props} onClick={handleLinkClick}>
      {children}
    </Link>
  );
}
