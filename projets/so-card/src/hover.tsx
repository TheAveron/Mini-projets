import { useRef, type JSX, type MouseEvent, type ReactNode } from "react";

function HoverEffectCard(type, content): JSX.Element {
    const elementRef = useRef<HTMLDivElement>(null);

    function rotateElement(event: MouseEvent): void {
        const element = elementRef.current;
        if (!element) return;

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
    }

    function handleMouseEnter(): void {
        document.addEventListener("mousemove", rotateElement);
    }

    function handleMouseLeave(): void {
        document.removeEventListener("mousemove", rotateElement);

        // Optional: reset the rotation
        const element = elementRef.current;
        if (element) {
            element.style.setProperty("--rotateX", "0deg");
            element.style.setProperty("--rotateY", "0deg");
        }
    }

    return (
        <div
            ref={elementRef}
            className={"card " + type}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {content}
        </div>
    );
}

export default HoverEffectCard;
