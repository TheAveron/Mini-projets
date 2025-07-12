import React from "react";
import HoverEffectCard from "./hover";

// ------------------ Types ------------------
interface BaseCard {
    name: string;
    type: string;
    cost?: Record<string, number>;
    effect?: string;
    bonus?: string;
    flavor?: string;
    tags?: string[];
    illustration?: string;
    limit?: string;
}

interface ShipCard extends BaseCard {
    type: "ship";
    range: number;
    cargo?: number;
}

interface PlanetCard extends BaseCard {
    type: "planet";
    distance: number;
    size: number;
    access?: string;
    income?: Record<string, number>;
    mission_bonus?: string;
    maxplayers?: number;
}

interface TechnologyCard extends BaseCard {
    type: "technology";
}

interface EventCard extends BaseCard {
    type: "event";
    duration: string;
}

export type CardData = ShipCard | PlanetCard | TechnologyCard | EventCard;

interface CardProps {
    card: CardData;
}

export interface CardListProps {
    gameData: {
        normal_cards: {
            ships: ShipCard[];
        };
        planet_cards: PlanetCard[];
        technology_cards: TechnologyCard[];
        event_cards: EventCard[];
    };
}

// ------------------ Card Component ------------------
const Card: React.FC<CardProps> = ({ card }) => {
    const renderStats = () => {
        if (card.type === "ship") {
            return (
                <div className="card-section">
                    <div className="card-label">Ship Stats</div>
                    <div className="card-stats">
                        <span>
                            Type:{" "}
                            {card.tags?.includes("Freight")
                                ? "Freight"
                                : card.tags?.includes("Peoples")
                                ? "People"
                                : "Unknown"}
                        </span>

                        <span>Range: {card.range ?? "?"}</span>
                        {card.cargo !== undefined && (
                            <span>Cargo: {card.cargo}</span>
                        )}
                    </div>
                </div>
            );
        } else if (card.type === "planet") {
            return (
                <div className="card-section">
                    <div className="card-label">Planet Stats</div>
                    <div className="card-stats">
                        <span>
                            Type:{" "}
                            {card.tags?.includes("Telluric")
                                ? "Telluric"
                                : card.tags?.includes("Gas giant")
                                ? "Gas giant"
                                : "Unknown"}
                        </span>
                        <span>Distance: {card.distance}</span>
                        <span>Size: {card.size}</span>
                        <span>Max Players: {card.maxplayers}</span>
                    </div>
                </div>
            );
        } else if (card.type === "event") {
            return (
                <div className="card-section">
                    <div className="card-label">Event Stats</div>
                    <div className="card-stats">
                        <span>Duration: {card.duration}</span>
                    </div>
                </div>
            );
        }
        /* else if (card.type === "technology") {
            return (
                <div className="card-section">
                    <div className="card-label">Tech Effect</div>
                    <div className="card-stats">{card.effect}</div>
                </div>
            );
        }*/
        return null;
    };

    const renderCost = () => {
        if (!card.cost) return null;
        return (
            <div className="card-cost">
                {Object.entries(card.cost).map(([resource, amount]) => (
                    <div
                        className="cost-badge"
                        key={resource}
                        title={`${amount} ${resource}`}
                    >
                        <img src="/Mini-projets/illustrations/icons/coin.png" />
                        {amount}
                    </div>
                ))}
            </div>
        );
    };

    const renderConstraints = () => {
        if (!card.limit) return null;
        return (
            <div className="card-section">
                <div className="card-label">Constraints</div>
                <div className="card-effect" style={{ whiteSpace: "pre-line" }}>
                    {card.limit}
                </div>
            </div>
        );
    };

    const renderBonus = () => {
        if (!card.bonus) return null;
        return (
            <div className="card-section">
                <div className="card-label">Bonus</div>
                <div className="card-effect" style={{ whiteSpace: "pre-line" }}>
                    {card.bonus}
                </div>
            </div>
        );
    };

    const renderEffect = () => {
        if (!card.effect) return null;
        return (
            <div className="card-section">
                <div className="card-label">Gains</div>
                <div className="card-effect" style={{ whiteSpace: "pre-line" }}>
                    {typeof card.effect === "string" ? (
                        <>{card.effect}</>
                    ) : card.effect && typeof card.effect === "object" ? (
                        Object.entries(card.effect).map(
                            ([resource, amount]) => (
                                <React.Fragment key={resource}>
                                    • {String(resource)}: {String(amount)}
                                </React.Fragment>
                            )
                        )
                    ) : null}
                </div>
            </div>
        );
    };

    return (
        <>
            <div
                className="card-art"
                style={{
                    backgroundImage: `url('${
                        card.illustration
                            ? `/Mini-projets/illustrations/${card.illustration}`
                            : `https://placehold.co/350x250?text=${card.name}`
                    }')`,
                }}
            >
                <div className="card-header">
                    <div className="header-left">
                        <img
                            className="card-type-icon"
                            src={
                                "/Mini-projets/illustrations/icons/" +
                                card.type +
                                ".png"
                            }
                        />
                        <div className="card-title">{card.name}</div>
                    </div>
                    {renderCost()}
                </div>
            </div>
            <div className="card-body">
                {renderStats()}
                {renderConstraints()}
                {renderEffect()}
                {renderBonus()}
                <div className="side-notes">
                    {card.tags && (
                        <div className="card-tags">
                            Tags: {card.tags.join(" • ")}
                        </div>
                    )}
                    {card.flavor && (
                        <div className="card-flavor">"{card.flavor}"</div>
                    )}
                </div>
            </div>
        </>
    );
};

// ------------------ CardList Component ------------------
const CardList: React.FC<CardListProps> = ({ gameData }) => {
    const cards: CardData[] = [
        ...gameData.normal_cards.ships,
        ...gameData.planet_cards,
        ...gameData.technology_cards,
        ...gameData.event_cards,
    ];

    return (
        <div className="card-list">
            {cards.map((card, index) =>
                HoverEffectCard(card.type, <Card card={card} key={index} />)
            )}
        </div>
    );
};

export default CardList;
