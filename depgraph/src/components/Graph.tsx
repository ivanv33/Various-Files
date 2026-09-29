"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import ForceGraph3D, { type ForceGraphMethods } from "react-force-graph-3d";
import { toGraphData, type GraphLink, type GraphNode } from "@/lib/graphData";
import type { Plan, Status } from "@/lib/schema";

export const STATUS_COLORS: Record<Status, string> = {
  todo: "#8b95a7",
  doing: "#5ac8fa",
  done: "#3a4152",
  blocked: "#ff6b6b",
};

interface GraphProps {
  plan: Plan;
  selectedId: string | null;
  linkMode: boolean;
  onSelect: (id: string | null) => void;
  onLinkRightClick: (dependencyId: string, dependentId: string) => void;
}

const idOf = (end: unknown) =>
  typeof end === "string" ? end : (end as GraphNode).id;

export default function Graph({
  plan,
  selectedId,
  linkMode,
  onSelect,
  onLinkRightClick,
}: GraphProps) {
  const cache = useRef(new Map<string, GraphNode>());
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(
    undefined,
  );
  const [size, setSize] = useState({ w: 800, h: 600 });

  useEffect(() => {
    const update = () =>
      setSize({ w: window.innerWidth, h: window.innerHeight });
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const structureKey = plan.nodes
    .map((n) => `${n.id}:${n.status}:${n.title}:${n.depends_on.join(",")}`)
    .join("|");
  const data = useMemo(() => toGraphData(plan, cache.current), [structureKey]); // eslint-disable-line react-hooks/exhaustive-deps

  const neighbors = useMemo(() => {
    const set = new Set<string>();
    if (!selectedId) return set;
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId)
        set.add(idOf(l.target));
      if (l.target === selectedId || idOf(l.target) === selectedId)
        set.add(idOf(l.source));
    }
    return set;
  }, [data, selectedId]);

  const nodeColor = (n: GraphNode) => {
    const base = STATUS_COLORS[n.status];
    if (!selectedId || n.id === selectedId || neighbors.has(n.id)) return base;
    return base + "33";
  };

  return (
    <div style={{ cursor: linkMode ? "crosshair" : "default" }}>
      <ForceGraph3D<GraphNode, GraphLink>
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#05060a"
        nodeLabel={(n: GraphNode) => `${n.title} · ${n.status}`}
        nodeColor={nodeColor}
        nodeRelSize={6}
        nodeOpacity={1}
        linkColor={() => "#7a8399"}
        linkOpacity={0.5}
        linkWidth={(l: GraphLink) =>
          selectedId &&
          (idOf(l.source) === selectedId || idOf(l.target) === selectedId)
            ? 2
            : 0.6
        }
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={(l: GraphLink) =>
          selectedId && idOf(l.target) === selectedId ? 2 : 0
        }
        onNodeClick={(n: GraphNode) => onSelect(n.id)}
        onBackgroundClick={() => onSelect(null)}
        onLinkRightClick={(l: GraphLink) =>
          onLinkRightClick(idOf(l.source), idOf(l.target))
        }
      />
    </div>
  );
}
