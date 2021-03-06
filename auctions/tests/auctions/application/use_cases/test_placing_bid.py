from unittest.mock import (
    Mock,
    patch,
)

import pytest

from auctions.application.use_cases import PlacingBidUseCase
from auctions.application.use_cases.placing_bid import PlacingBidInputDto, PlacingBidOutputDto
from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.factories import get_dollars
from auctions.domain.value_objects import Money


@pytest.fixture()
def bidder_id() -> int:
    return 1


@pytest.fixture()
def amount() -> Money:
    return get_dollars('10.00')


@pytest.fixture()
def input_dto(exemplary_auction_id: int, bidder_id: int, amount: Money) -> PlacingBidInputDto:
    return PlacingBidInputDto(bidder_id, exemplary_auction_id, amount)


def test_loads_auction_using_id(
        exemplary_auction_id: int,
        auctions_repo_mock: Mock,
        input_dto: PlacingBidInputDto
) -> None:
    PlacingBidUseCase().execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(exemplary_auction_id)


def test_makes_an_expected_bid(
        input_dto: PlacingBidInputDto,
        auction: Auction
) -> None:
    with patch.object(Auction, 'make_a_bid', wraps=auction.make_a_bid) as make_a_bid_mock:
        PlacingBidUseCase().execute(input_dto)

    make_a_bid_mock.assert_called_once_with(
        Bid(id=None, amount=input_dto.amount, bidder_id=input_dto.bidder_id)
    )


def test_saves_auction(
        auctions_repo_mock: Mock,
        auction: Auction,
        input_dto: PlacingBidInputDto
) -> None:
    PlacingBidUseCase().execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_notifies_winner(
        email_gateway_mock: Mock,
        auction: Auction,
        input_dto: PlacingBidInputDto
) -> None:
    PlacingBidUseCase().execute(input_dto)

    email_gateway_mock.notify_about_winning_auction.assert_called_once_with(input_dto.auction_id, input_dto.bidder_id)


def test_presents_output_dto(
        input_dto: PlacingBidInputDto,
        placing_bid_output_boundary_mock: Mock,
        auction: Auction,
) -> None:
    PlacingBidUseCase().execute(input_dto)

    desired_output_dto = PlacingBidOutputDto(is_winner=True, current_price=input_dto.amount)
    placing_bid_output_boundary_mock.present.assert_called_once_with(desired_output_dto)
