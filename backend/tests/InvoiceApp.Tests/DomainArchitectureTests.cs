using System.Reflection;
using InvoiceApp.Domain;
using Xunit;

namespace InvoiceApp.Tests;

/// <summary>
/// Structural rule from AGENTS.md: the Domain project holds business rules only,
/// with no web or storage code, and never depends on the Api project.
/// </summary>
public class DomainArchitectureTests
{
    private static readonly string[] ForbiddenAssemblyPrefixes =
    {
        "InvoiceApp.Api",
        "Microsoft.AspNetCore",
        "Microsoft.EntityFrameworkCore",
        "Microsoft.Data.SqlClient",
        "System.Data.SqlClient",
        "Azure.Messaging.ServiceBus",
        "System.Net.Http",
    };

    [Fact]
    public void DomainAssembly_DependsOnNeitherWebNorStorageNorMessagingCode()
    {
        var domainAssembly = typeof(ApprovalService).Assembly;

        var violations = FindForbiddenReferences(domainAssembly);

        Assert.True(
            violations.Count == 0,
            "InvoiceApp.Domain must not reference web, storage or messaging assemblies, but references: "
            + string.Join(", ", violations));
    }

    private static List<string> FindForbiddenReferences(Assembly assembly) =>
        assembly.GetReferencedAssemblies()
            .Select(reference => reference.Name ?? string.Empty)
            .Where(name => ForbiddenAssemblyPrefixes.Any(prefix =>
                name.StartsWith(prefix, StringComparison.Ordinal)))
            .OrderBy(name => name, StringComparer.Ordinal)
            .ToList();
}
