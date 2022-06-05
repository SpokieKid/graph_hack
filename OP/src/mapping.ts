import { BigInt } from "@graphprotocol/graph-ts"
import {
  Token,
  Approval,
  DelegateChanged,
  DelegateVotesChanged,
  OwnershipTransferred,
  Transfer
} from "../generated/Token/Token"
import { Transaction } from "../generated/schema"

export function handleTransfer (event: Transfer): void {
  let transaction = new Transaction(event.transaction.hash.toHex())
  transaction.from = event.params.from
  transaction.to = event.params.to
  transaction.amount = event.params.value
  transaction.save()
}
