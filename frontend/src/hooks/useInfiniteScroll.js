import { useEffect, useRef } from "react";

export function useInfiniteScroll(onLoadMore, enabled = true) {
  const ref = useRef(null);

  useEffect(() => {
    if (!enabled || !ref.current) return undefined;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          onLoadMore();
        }
      },
      { threshold: 0.6 }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [enabled, onLoadMore]);

  return ref;
}
