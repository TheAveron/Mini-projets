import CardList from "./cards_gen";
import gameDataRaw from "./assets/cards.json";
import { type CardListProps } from "./cards_gen"; // You may need to export the interface
import "./App.css";

const gameData: CardListProps["gameData"] = {
    ...gameDataRaw,
    normal_cards: {
        ...gameDataRaw.normal_cards,
        ships: gameDataRaw.normal_cards.ships.map((ship: any) => ({
            ...ship,
            type: "ship" as const,
        })),
    },
    planet_cards: gameDataRaw.planet_cards.map((planet: any) => ({
        ...planet,
        type: "planet" as const,
    })),
    technology_cards: gameDataRaw.technology_cards.map((tech: any) => ({
        ...tech,
        type: "technology" as const,
    })),
    event_cards: gameDataRaw.event_cards.map((event: any) => ({
        ...event,
        type: "event" as const,
    })),
};

function App() {
    return (
        <div className="App">
            <div
                style={{
                    display: "flex",
                    flexDirection: "row",
                    placeContent: "space-between",
                    alignItems: "center",
                }}
            >
                <h1>Stellar Odyssey - The Card game </h1>
                <a href="style_guide">Design guide</a>
            </div>
            <br />
            <h2>Gallery</h2>
            <CardList gameData={gameData} />
        </div>
    );
}

export default App;
