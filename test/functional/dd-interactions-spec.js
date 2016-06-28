'use strict';

var SettlementPage = require( './settlementAidOfferPage.js' );

fdescribe( 'The college costs worksheet page', function() {
  var page;
  var EC = protractor.ExpectedConditions;

  beforeEach(function() {
    page = new SettlementPage();
  } );

  // Private loan interactions

  it( 'should add a private loan entry when the add button is clicked', function() {
    var count;
    page.confirmVerification();
    browser.sleep( 1000 );
    page.addPrivateLoanButton.click();
    count = element.all( by.css( '.private-loans .private-loans_loan' ) ).count();
    expect( count ).toBe( 2 );
  } );

  it( 'should remove a private loan entry when the loan\'s remove button is clicked', function() {
    var count;
    page.confirmVerification();
    browser.sleep( 1000 );
    element.all( by.css( '.private-loans .private-loans_loan'))
      .last().all( by.css( '.private-loans_remove-btn' ) ).click();
    count = element.all( by.css( '.private-loans .private-loans_loan' ) ).count();
    expect( count ).toBe( 0 );
  } );

  it( 'should add a private loan even after the last private loan is removed', function() {
    var count;
    page.confirmVerification();
    browser.sleep( 1000 );
    element.all( by.css( '.private-loans .private-loans_loan'))
      .last().all( by.css( '.private-loans_remove-btn' ) ).click();
    page.addPrivateLoanButton.click();
    count = element.all( by.css( '.private-loans .private-loans_loan' ) ).count();
    expect( count ).toBe( 1 );
  } );

  // Loan repayment toggle interactions

  it( 'should show the loan payment toggles in Step 2 if federal loans are over $30k', function() {
    page.setProgramLength( 6 );
    page.confirmVerification();
    browser.actions().mouseMove(page.subsidizedLoans).perform();
    page.setSubsidizedLoans( 3500 );
    browser.actions().mouseMove(page.unsubsidizedLoans).perform();
    page.setUnsubsidizedLoans( 6000 );
    browser.sleep( 1000 );
    page.continueStep2();
    browser.actions().mouseMove(page.monthlyPaymentLoanLengthToggles).perform();
    expect( page.monthlyPaymentLoanLengthToggles.isDisplayed() ).toBeTruthy();
    browser.actions().mouseMove(page.debtBurdenLoanLengthToggles).perform();
    expect( page.debtBurdenLoanLengthToggles.isDisplayed() ).toBeTruthy();
  } );

  it( 'should hide the loan payment toggles in Step 2 if federal loans are $30k or less', function() {
    page.setProgramLength( 2 );
    page.confirmVerification();
    browser.actions().mouseMove(page.subsidizedLoans).perform();
    page.setSubsidizedLoans( 1000 );
    browser.actions().mouseMove(page.unsubsidizedLoans).perform();
    page.setUnsubsidizedLoans( 1000 );
    browser.sleep( 1000 );
    page.continueStep2();
    browser.actions().mouseMove(page.monthlyPaymentLoanLengthToggles).perform();
    expect( page.monthlyPaymentLoanLengthToggles.isDisplayed() ).toBeFalsy();
    browser.actions().mouseMove(page.debtBurdenLoanLengthToggles).perform();
    expect( page.debtBurdenLoanLengthToggles.isDisplayed() ).toBeFalsy();
  } );

  it( 'should show correct loan payment values for 10 yrs when toggled', function() {

  } );

  it( 'should show correct loan payment values 25 yrs when toggled', function() {

  } );

  it( 'should change one loan payment toggle if the other is changed', function() {
    page.setProgramLength( 6 );
    page.confirmVerification();
    browser.actions().mouseMove( page.subsidizedLoans ).perform();
    page.setSubsidizedLoans( 3500 );
    browser.actions().mouseMove( page.unsubsidizedLoans ).perform();
    page.setUnsubsidizedLoans( 6000 );
    browser.sleep( 1000 );
    page.continueStep2();
    page.toggleMonthlyPaymentLoanLengthTo25Yrs();
    browser.actions().mouseMove( page.debtBurdenLoan25YrsToggle ).perform();
    browser.sleep( 2000 );
    expect( page.debtBurdenLoan25YrsToggle.isSelected() ).toBeTruthy();
  } );

} );
