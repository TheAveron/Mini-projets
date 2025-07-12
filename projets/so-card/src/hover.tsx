import { useRef, type JSX } from "react";

function HoverEffectCard(type: string, content: JSX.Element): JSX.Element {
    const elementRef = useRef<HTMLDivElement>(null);
    const glareRef = useRef<HTMLDivElement>(null);

    function rotateElement(event: globalThis.MouseEvent): void {
        const element = elementRef.current;
        const glare = glareRef.current;
        if (!element || !glare) return;

        const rect = element.getBoundingClientRect();

        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const middleX = rect.width / 2;
        const middleY = rect.height / 2;

        const offsetX = (x - middleX) / middleX;
        const offsetY = (y - middleY) / middleY;

        const rotateX = -offsetY * 15;
        const rotateY = offsetX * 15;

        element.style.setProperty("--rotateX", rotateX + "deg");
        element.style.setProperty("--rotateY", rotateY + "deg");

        // Update glare position
        const percentX = (x / rect.width) * 100;
        const percentY = (y / rect.height) * 100;
        glare.style.background = `radial-gradient(circle at ${percentX}% ${percentY}%, rgba(255,255,255,0.4), transparent 60%)`;
        glare.style.opacity = "1";
    }

    function handleMouseEnter(): void {
        document.addEventListener("mousemove", rotateElement);
    }

    function handleMouseLeave(): void {
        document.removeEventListener("mousemove", rotateElement);

        const element = elementRef.current;
        const glare = glareRef.current;

        if (element) {
            element.style.setProperty("--rotateX", "0deg");
            element.style.setProperty("--rotateY", "0deg");
        }

        if (glare) {
            glare.style.opacity = "0";
        }
    }

    return (
        <div
            ref={elementRef}
            className={"card " + type}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <div className="glare" ref={glareRef}></div>
            {content}
        </div>
    );
}

export default HoverEffectCard;
