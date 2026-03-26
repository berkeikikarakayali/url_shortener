from user_agents import parse


class DeviceService:
    @staticmethod
    def parse_user_agent(user_agent_string: str | None) -> dict:
        if not user_agent_string:
            return {
                "device_type": "unknown",
                "browser": "unknown"
            }

        user_agent = parse(user_agent_string)

        if user_agent.is_mobile:
            device_type = "mobile"
        elif user_agent.is_tablet:
            device_type = "tablet"
        elif user_agent.is_pc:
            device_type = "desktop"
        elif user_agent.is_bot:
            device_type = "bot"
        else:
            device_type = "unknown"

        browser = user_agent.browser.family or "unknown"

        return {
            "device_type": device_type,
            "browser": browser
        }