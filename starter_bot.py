class Bot:

    # ---------------------------------------------------------
    # PART 1: Find the average value of unseen cards
    # ---------------------------------------------------------
    def remaining_average(self, obs):

        unseen = obs["unseen"]

        total_cards = sum(unseen)

        if total_cards == 0:
            return 0

        total_value = 0

        # unseen[0] = number of Aces
        # unseen[1] = number of 2s
        # ...
        # unseen[12] = number of Kings

        for i in range(13):
            rank = i + 1
            count = unseen[i]

            total_value += rank * count

        return total_value / total_cards


    # ---------------------------------------------------------
    # PART 2: Estimate final value of the 15 cards
    # ---------------------------------------------------------
    def fair_value(self, obs):

        # Value of cards we know
        known_value = (
            sum(obs["hand"])
            + sum(obs["board"])
        )

        # Number of cards we already know
        known_cards = (
            len(obs["hand"])
            + len(obs["board"])
        )

        # There are always 15 cards in total:
        # 5 our cards + 5 opponent cards + 5 board cards
        unknown_cards = 15 - known_cards

        # Average value of an unknown card
        avg_remaining = self.remaining_average(obs)

        # Estimate the final stock value
        fair = (
            known_value
            + unknown_cards * avg_remaining
        )

        return fair


    # ---------------------------------------------------------
    # PART 3: Decide whether to PEEK or SWAP
    # ---------------------------------------------------------
    def move(self, obs):

        # Do not make a move in the final round
        if obs["round"] >= 5:
            return None

        # SWAP can only be used once per deal.
        # If there is already a discard, we have used it.
        if len(obs["discards"]) > 0:
            return None

        # Find our lowest card
        lowest_index = min(
            range(5),
            key=lambda i: obs["hand"][i]
        )

        lowest_card = obs["hand"][lowest_index]

        # If we have a very weak card,
        # replace it with a new secret card.
        if lowest_card <= 4:
            return ("SWAP", lowest_index)

        # Otherwise do nothing
        return None


    # ---------------------------------------------------------
    # PART 4: Give our price when we are the maker
    # ---------------------------------------------------------
    def quote(self, obs):

        fair = self.fair_value(obs)

        return fair


    # ---------------------------------------------------------
    # PART 5: Decide what to do with opponent's quote
    # ---------------------------------------------------------
    def respond(self, obs, price):

        # Our estimate of the final stock value
        fair = self.fair_value(obs)

        # Actual prices at which we can trade
        buy_price = price + 2
        sell_price = price - 2

        # Our current position
        position = obs["position"]

        # Require some advantage before trading
        EDGE = 1.5


        # -----------------------------------------------------
        # BUY
        # -----------------------------------------------------
        #
        # If the opponent lets us buy below our estimated value,
        # we think the asset is cheap.
        #
        if buy_price < fair - EDGE:

            # Maximum trade size is 2.
            # Position cannot become greater than +10.
            amount = min(
                2,
                10 - position
            )

            if amount > 0:
                return amount


        # -----------------------------------------------------
        # SELL
        # -----------------------------------------------------
        #
        # If the opponent lets us sell above our estimated value,
        # we think the asset is expensive.
        #
        if sell_price > fair + EDGE:

            # Maximum trade size is 2.
            # Position cannot become less than -10.
            amount = min(
                2,
                10 + position
            )

            if amount > 0:
                return -amount


        # -----------------------------------------------------
        # PASS
        # -----------------------------------------------------
        return 0
