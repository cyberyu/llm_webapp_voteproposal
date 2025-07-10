// UPL LIMITED Selection Simulation
// This demonstrates what happens when "UPL LIMITED" is selected in both dropdown boxes

console.log("=== UPL LIMITED DROPDOWN SELECTION SIMULATION ===");

// Simulated data from filtered_proposals.csv (peer analysis dataset)
const uplPeerData = [
    {
        proposal_master_skey: "2262775",
        job_number: "Z89786", 
        issuer_name: "UPL LIMITED",
        service: "BN",
        record_date: "3/31/2025",
        mgmt_rec: "F",
        proposal: "To approve material related party transactions pertaining to sale of materials by UPL Do Brasil - Industria e Comércio de Insumos Agropecuários S.A. to Associates",
        proposal_type: "MG",
        Category: "Corporate Structure",
        Subcategory: "Golden Parachutes",
        ForRatioAmongVoted: 1.0,
        ForRatioAmongElig: 0.374077471,
        VotingRatio: 0.374077471
    },
    // ... 18 more similar records with same pattern
];

// Summary Statistics when UPL LIMITED is selected
const uplSummary = {
    totalProposals: 19,
    uniqueJobNumbers: ["Z89786"],
    uniqueServices: ["BN"],
    uniqueRecordDates: ["3/31/2025"],
    uniqueMgmtRecs: ["F"],
    avgForRatioVoted: 1.0,
    avgForRatioEligible: 0.374077471,
    avgVotingRatio: 0.374077471,
    categories: {
        "Corporate Structure": 10,
        "Shareholder Rights": 6,
        "Board of Directors": 3
    },
    subcategories: {
        "Golden Parachutes": 7,
        "Supermajority Voting": 5,
        "Antitakeover Provisions": 5,
        "Omnibus Stock Plan": 1,
        "Director Remuneration": 1
    }
};

console.log("📊 SUMMARY TABLE CONTENT FOR UPL LIMITED:");
console.log("==========================================");
console.log(`Total Proposals: ${uplSummary.totalProposals}`);
console.log(`Job Numbers: ${uplSummary.uniqueJobNumbers.join(', ')}`);
console.log(`Services: ${uplSummary.uniqueServices.join(', ')}`);
console.log(`Record Dates: ${uplSummary.uniqueRecordDates.join(', ')}`);
console.log(`Management Recommendations: ${uplSummary.uniqueMgmtRecs.join(', ')}`);
console.log(`Average For Ratio (Voted): ${(uplSummary.avgForRatioVoted * 100).toFixed(1)}%`);
console.log(`Average For Ratio (Eligible): ${(uplSummary.avgForRatioEligible * 100).toFixed(1)}%`);
console.log(`Average Voting Ratio: ${(uplSummary.avgVotingRatio * 100).toFixed(1)}%`);

console.log("\n📋 CATEGORY BREAKDOWN:");
Object.entries(uplSummary.categories).forEach(([category, count]) => {
    console.log(`  ${category}: ${count} proposals`);
});

console.log("\n🏷️ SUBCATEGORY BREAKDOWN:");
Object.entries(uplSummary.subcategories).forEach(([subcategory, count]) => {
    console.log(`  ${subcategory}: ${count} proposals`);
});

console.log("\n💡 KEY INSIGHTS:");
console.log("• All proposals have the same record date (3/31/2025)");
console.log("• All proposals have the same job number (Z89786)");
console.log("• All proposals are service type 'BN' (Ballot Navigator)");
console.log("• All have management recommendation 'F' (For)");
console.log("• 100% For Ratio among voted shares");
console.log("• 37.4% For Ratio among eligible shares");
console.log("• 37.4% Voting participation ratio");
console.log("• Focus on related party transactions and director appointments");

console.log("\n🔍 WHAT THE TABLE WOULD SHOW:");
console.log("When both dropdowns are set to 'UPL LIMITED', the Summary Table displays:");
console.log("1. Aggregated statistics from both datasets");
console.log("2. List of all unique record dates");
console.log("3. List of all unique job numbers");
console.log("4. List of all unique services");
console.log("5. Management recommendation breakdown");
console.log("6. Average approval rates and voting participation");
console.log("7. Complete list of all proposals for the selected issuer");
