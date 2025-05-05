from typing import Dict, Callable, Any
from dataclasses import dataclass
from modules.logger import logger

@dataclass
class DebugCommand:
    """Debug command configuration"""
    name: str
    handler: Callable[[Dict[str, Any]], None]
    description: str

class DebugPanel:
    """Debug panel functionality"""
    def __init__(self, game_state: Dict[str, Any]):
        self.state = game_state
        self.commands = self._setup_commands()

    def _setup_commands(self) -> Dict[str, DebugCommand]:
        return {
            "1": DebugCommand("Add RP", self._add_rp, "Add Reflection Points"),
            "2": DebugCommand("Set HP", self._set_hp, "Modify current HP"),
            "3": DebugCommand("Force Mutation", self._force_mutation, "Trigger mutation event"),
            "4": DebugCommand("Force Disaster", self._force_disaster, "Trigger disaster event"),
            "5": DebugCommand("Collapse Now", self._force_collapse, "Force game over")
        }

    def show(self) -> None:
        """Display debug panel and handle input"""
        print("\n=== DEBUG PANEL ===")
        for key, cmd in self.commands.items():
            print(f"{key}. {cmd.name}")
        print("Press Enter to cancel.")

        if choice := input("Choice: ").strip():
            if cmd := self.commands.get(choice):
                try:
                    cmd.handler(self.state)
                except Exception as e:
                    logger.error(f"Debug command failed: {e}")

    def _add_rp(self, state: Dict[str, Any]) -> None:
        if amt := input("Add how many RP? ").strip():
            if amt.isdigit():
                state["rp"] += int(amt)
                logger.debug(f"Added {amt} RP")

    def _set_hp(self, state: Dict[str, Any]) -> None:
        if amt := input("Set HP to: ").strip():
            if amt.isdigit():
                state["hp"] = min(int(amt), 100)
                logger.debug(f"Set HP to {amt}")

    def _force_mutation(self, state: Dict[str, Any]) -> None:
        print("🧬 Triggering mutation...")
        result = state["handle_mutation_event"](state["traits"], state["mutations"], state["mutation_rate"])
        state["mutations"].append({
            "name": result["mutation"].split(" — ")[0],
            "effect": result["generated"]
        })
        state["hp"], state["mutation_rate"] = state["apply_mutation_stats"](
            state["hp"], state["mutation_rate"], result["effects"]
        )
        state["rp"] += result["rp_reward"]
        logger.debug("Mutation triggered")

    def _force_disaster(self, state: Dict[str, Any]) -> None:
        print("🌪 Triggering disaster...")
        damage = state["handle_disaster_event"](state["hp"], state["resistance"], state["survival_seconds"])
        state["hp"] -= damage["damage"]
        state["rp"] += damage["rp_reward"]
        logger.debug("Disaster triggered")

    def _force_collapse(self, state: Dict[str, Any]) -> None:
        state["hp"] = 0
        logger.debug("Forced collapse")
